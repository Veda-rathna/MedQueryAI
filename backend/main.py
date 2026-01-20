"""
Main FastAPI Application - Drug Information Chatbot Backend
Provides REST API for PDF upload, ingestion, and querying
"""
import os
import uuid
import shutil
import json
import hashlib
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
documents_metadata = {}  # document_id -> {filename, hash, upload_date, page_count, chunk_count}

# Metadata file path
METADATA_FILE = os.path.join(config.UPLOAD_DIR, "documents_metadata.json")


# Helper functions
def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def save_metadata():
    """Save documents metadata to disk"""
    with open(METADATA_FILE, "w") as f:
        json.dump(documents_metadata, f, indent=2)


def load_metadata():
    """Load documents metadata from disk"""
    global documents_metadata
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            documents_metadata = json.load(f)


def find_duplicate_by_hash(file_hash: str) -> Optional[str]:
    """Find document ID if file with same hash exists"""
    for doc_id, metadata in documents_metadata.items():
        if metadata.get("hash") == file_hash:
            return doc_id
    return None


def load_existing_documents():
    """Load all existing documents on startup"""
    load_metadata()
    
    for doc_id, metadata in documents_metadata.items():
        try:
            # Load vector store
            store = VectorStore.load(config.VECTOR_STORE_DIR, doc_id)
            vector_stores[doc_id] = store
            
            # Create retriever
            retriever = create_retriever(store, memory)
            retrievers[doc_id] = retriever
            
            print(f"Loaded document: {metadata['filename']} (ID: {doc_id})")
        except Exception as e:
            print(f"Warning: Failed to load document {doc_id}: {e}")


@app.on_event("startup")
async def startup_event():
    """Load existing documents on server startup"""
    print("=" * 60)
    print("Starting Drug Information Chatbot API...")
    print(f"LM Studio endpoint: {config.LM_STUDIO_BASE_URL}")
    print(f"Embedding model: {config.EMBEDDING_MODEL}")
    print("=" * 60)
    print("\nLoading existing documents...")
    load_existing_documents()
    print(f"✓ Successfully loaded {len(vector_stores)} documents")
    
    if len(vector_stores) > 0:
        print("\nAvailable documents:")
        for doc_id, metadata in documents_metadata.items():
            print(f"  - {metadata['filename']} (ID: {doc_id[:8]}...)")
    else:
        print("\n⚠ No documents found. Upload a PDF to get started!")
    print("=" * 60)


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
    Upload and process a PDF file (checks for duplicates)
    
    Args:
        file: PDF file upload
    
    Returns:
        Upload response with document ID and processing stats
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save to temporary location first
    temp_id = str(uuid.uuid4())
    temp_path = os.path.join(config.UPLOAD_DIR, f"temp_{temp_id}.pdf")
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Calculate file hash to check for duplicates
        file_hash = calculate_file_hash(temp_path)
        
        # Check if file already exists
        existing_doc_id = find_duplicate_by_hash(file_hash)
        if existing_doc_id:
            os.remove(temp_path)  # Remove temp file
            metadata = documents_metadata[existing_doc_id]
            raise HTTPException(
                status_code=409, 
                detail=f"Duplicate file detected. This file already exists as '{metadata['filename']}'"
            )
        
        # Generate document ID and move to permanent location
        document_id = str(uuid.uuid4())
        upload_path = os.path.join(config.UPLOAD_DIR, f"{document_id}.pdf")
        shutil.move(temp_path, upload_path)
        
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
        
        # Save metadata
        documents_metadata[document_id] = {
            "filename": file.filename,
            "hash": file_hash,
            "upload_date": datetime.now().isoformat(),
            "page_count": page_count,
            "chunk_count": chunk_count
        }
        save_metadata()
        
        print(f"Successfully processed {file.filename}: {page_count} pages, {chunk_count} chunks")
        
        return UploadResponse(
            document_id=document_id,
            filename=file.filename,
            page_count=page_count,
            chunk_count=chunk_count,
            message="PDF processed successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if 'upload_path' in locals() and os.path.exists(upload_path):
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
    List all available documents with metadata
    
    Returns:
        List of documents with details
    """
    documents = []
    for doc_id, metadata in documents_metadata.items():
        documents.append({
            "document_id": doc_id,
            "filename": metadata.get("filename", "Unknown"),
            "upload_date": metadata.get("upload_date", "Unknown"),
            "page_count": metadata.get("page_count", 0),
            "chunk_count": metadata.get("chunk_count", 0)
        })
    
    # Sort by upload date (newest first)
    documents.sort(key=lambda x: x["upload_date"], reverse=True)
    
    return {
        "documents": documents,
        "count": len(documents)
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
    if document_id not in documents_metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    
    filename = documents_metadata[document_id].get("filename", "Unknown")
    
    # Remove from global state
    if document_id in vector_stores:
        del vector_stores[document_id]
    if document_id in retrievers:
        del retrievers[document_id]
    
    # Delete metadata
    del documents_metadata[document_id]
    save_metadata()
    
    # Delete PDF file
    upload_path = os.path.join(config.UPLOAD_DIR, f"{document_id}.pdf")
    if os.path.exists(upload_path):
        os.remove(upload_path)
    
    # Delete vector store files
    vector_store_path = os.path.join(config.VECTOR_STORE_DIR, f"{document_id}.faiss")
    metadata_path = os.path.join(config.VECTOR_STORE_DIR, f"{document_id}.pkl")
    if os.path.exists(vector_store_path):
        os.remove(vector_store_path)
    if os.path.exists(metadata_path):
        os.remove(metadata_path)
    
    print(f"Deleted document: {filename} (ID: {document_id})")
    
    return {
        "message": f"Document '{filename}' deleted successfully",
        "document_id": document_id
    }


if __name__ == "__main__":
    import uvicorn
    
    print("Starting Drug Information Chatbot API...")
    print(f"LM Studio endpoint: {config.LM_STUDIO_BASE_URL}")
    print(f"Embedding model: {config.EMBEDDING_MODEL}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
