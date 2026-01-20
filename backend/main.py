"""
Main FastAPI Application - Drug Information Chatbot Backend
Provides REST API for PDF upload, ingestion, and querying
"""
import os
import uuid
import shutil
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

# Import our modules
from ingest_pdf import ingest_pdf
from chunking import chunk_pages
from vectorstore import VectorStore, create_vector_store
from memory import ConversationMemory, get_memory
from retrieval import RAGRetriever, create_retriever
from llm_client import test_connection
import config

# Initialize FastAPI app
app = FastAPI(
    title="Drug Information Chatbot API",
    description="Regulatory-grade chatbot for FDA prescribing information PDFs",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
vector_stores = {}  # document_id -> VectorStore
retrievers = {}     # document_id -> RAGRetriever
memory = get_memory()


# Request/Response Models
class ChatRequest(BaseModel):
    question: str
    session_id: str
    document_id: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    session_id: str
    timestamp: str


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    page_count: int
    chunk_count: int
    message: str


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]


class StatusResponse(BaseModel):
    status: str
    message: str
    lm_studio_connected: bool


# Endpoints
@app.get("/", response_model=StatusResponse)
async def root():
    """Health check and status endpoint"""
    lm_connected = test_connection()
    
    return StatusResponse(
        status="operational" if lm_connected else "degraded",
        message="Drug Information Chatbot API is running",
        lm_studio_connected=lm_connected
    )


@app.get("/health", response_model=StatusResponse)
async def health_check():
    """Detailed health check"""
    lm_connected = test_connection()
    
    return StatusResponse(
        status="healthy" if lm_connected else "unhealthy",
        message="LM Studio connection " + ("successful" if lm_connected else "failed"),
        lm_studio_connected=lm_connected
    )


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF file
    
    Args:
        file: PDF file upload
    
    Returns:
        Upload response with document ID and processing stats
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Generate document ID
    document_id = str(uuid.uuid4())
    
    # Save uploaded file
    upload_path = os.path.join(config.UPLOAD_DIR, f"{document_id}.pdf")
    
    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process PDF
        print(f"Processing PDF: {file.filename}")
        
        # Ingest
        pages = ingest_pdf(upload_path)
        page_count = len(pages)
        
        # Chunk
        chunks = chunk_pages(pages)
        chunk_count = len(chunks)
        
        # Create vector store
        store = create_vector_store(chunks)
        
        # Save vector store
        store.save(config.VECTOR_STORE_DIR, document_id)
        
        # Store in global state
        vector_stores[document_id] = store
        
        # Create retriever
        retriever = create_retriever(store, memory)
        retrievers[document_id] = retriever
        
        print(f"Successfully processed {file.filename}: {page_count} pages, {chunk_count} chunks")
        
        return UploadResponse(
            document_id=document_id,
            filename=file.filename,
            page_count=page_count,
            chunk_count=chunk_count,
            message="PDF processed successfully"
        )
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(upload_path):
            os.remove(upload_path)
        
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Answer a question using RAG
    
    Args:
        request: Chat request with question, session_id, and document_id
    
    Returns:
        Chat response with answer and sources
    """
    # Validate document ID
    if request.document_id not in retrievers:
        raise HTTPException(status_code=404, detail="Document not found. Please upload a PDF first.")
    
    try:
        # Get retriever
        retriever = retrievers[request.document_id]
        
        # Answer question
        result = retriever.answer_question(request.question, request.session_id)
        
        return ChatResponse(
            answer=result['answer'],
            sources=result['sources'],
            session_id=result['session_id'],
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


@app.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str):
    """
    Get conversation history for a session
    
    Args:
        session_id: Session identifier
    
    Returns:
        History response with messages
    """
    history = memory.get_history(session_id)
    
    return HistoryResponse(
        session_id=session_id,
        messages=history
    )


@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """
    Clear conversation history for a session
    
    Args:
        session_id: Session identifier
    
    Returns:
        Status message
    """
    memory.clear_session(session_id)
    
    return {"message": f"History cleared for session {session_id}"}


@app.get("/documents")
async def list_documents():
    """
    List all available documents
    
    Returns:
        List of document IDs
    """
    return {
        "documents": list(vector_stores.keys()),
        "count": len(vector_stores)
    }


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and its associated data
    
    Args:
        document_id: Document identifier
    
    Returns:
        Status message
    """
    if document_id not in vector_stores:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Remove from global state
    del vector_stores[document_id]
    del retrievers[document_id]
    
    # Delete files
    upload_path = os.path.join(config.UPLOAD_DIR, f"{document_id}.pdf")
    if os.path.exists(upload_path):
        os.remove(upload_path)
    
    return {"message": f"Document {document_id} deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    
    print("Starting Drug Information Chatbot API...")
    print(f"LM Studio endpoint: {config.LM_STUDIO_BASE_URL}")
    print(f"Embedding model: {config.EMBEDDING_MODEL}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
