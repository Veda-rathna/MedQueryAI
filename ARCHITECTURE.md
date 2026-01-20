# 📊 System Architecture Documentation

## Overview

The Drug Information Chatbot is a Retrieval-Augmented Generation (RAG) system designed for healthcare-safe question answering from FDA prescribing information PDFs.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Upload     │  │     Chat     │  │  Disclaimer  │     │
│  │    Panel     │  │    Panel     │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│            │                │                               │
│            └────────────────┴─────────> API Service        │
└────────────────────────────│────────────────────────────────┘
                              │ HTTP/REST
┌─────────────────────────────┴────────────────────────────────┐
│                      BACKEND (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   API Endpoints                       │   │
│  │  /upload  /chat  /history  /health  /documents      │   │
│  └────────────┬──────────────────────────────┬─────────┘   │
│               │                               │              │
│  ┌────────────▼──────────┐     ┌─────────────▼──────────┐  │
│  │   Ingestion Pipeline  │     │    RAG Pipeline         │  │
│  │  ┌──────────────────┐ │     │  ┌──────────────────┐  │  │
│  │  │  PDF Extractor   │ │     │  │   Retrieval      │  │  │
│  │  │   (PyMuPDF)      │ │     │  │  (Vector Search) │  │  │
│  │  └────────┬─────────┘ │     │  └────────┬─────────┘  │  │
│  │           │            │     │           │             │  │
│  │  ┌────────▼─────────┐ │     │  ┌────────▼─────────┐  │  │
│  │  │  Smart Chunker   │ │     │  │    Memory        │  │  │
│  │  │  (400-700 tokens)│ │     │  │  (Session Hist)  │  │  │
│  │  └────────┬─────────┘ │     │  └────────┬─────────┘  │  │
│  │           │            │     │           │             │  │
│  │  ┌────────▼─────────┐ │     │  ┌────────▼─────────┐  │  │
│  │  │ Embedding Model  │ │     │  │   LLM Client     │  │  │
│  │  │  (MiniLM-L6-v2)  │ │     │  │  (LM Studio)     │  │  │
│  │  └────────┬─────────┘ │     │  └──────────────────┘  │  │
│  │           │            │     │                         │  │
│  │  ┌────────▼─────────┐ │     │                         │  │
│  │  │  Vector Store    │ │     │                         │  │
│  │  │     (FAISS)      │◄┼─────┘                         │  │
│  │  └──────────────────┘ │                               │  │
│  └───────────────────────┘                               │  │
└───────────────────────────────────────────────────────────┘
                              │
                              │ HTTP API
┌─────────────────────────────▼────────────────────────────────┐
│                        LM STUDIO                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Mistral-7B-Instruct-v0.2 (Q4_K_S)         │   │
│  │                    Local Inference                    │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend (React + Tailwind)

#### Components
- **UploadPanel**: Drag-and-drop PDF upload with progress tracking
- **ChatPanel**: Conversation interface with example questions
- **ChatMessage**: Individual message rendering with citation highlighting
- **Disclaimer**: Healthcare safety warning (always visible)

#### Features
- Real-time processing feedback
- Markdown rendering
- Citation highlighting (clickable page references)
- Special highlighting for:
  - Dosages (blue)
  - Warnings (red)
  - Contraindications (orange)

#### State Management
- Session ID: Generated per browser session (UUID)
- Document ID: Received from backend after upload
- Message history: Local state (synced with backend)

### 2. Backend (Python + FastAPI)

#### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/health` | GET | Detailed status |
| `/upload` | POST | Upload and process PDF |
| `/chat` | POST | Answer question |
| `/history/{session_id}` | GET | Get conversation history |
| `/history/{session_id}` | DELETE | Clear history |
| `/documents` | GET | List documents |
| `/documents/{doc_id}` | DELETE | Delete document |

#### Core Modules

##### `ingest_pdf.py`
- **Purpose**: Extract text from PDF while preserving structure
- **Technology**: PyMuPDF (fitz)
- **Output**: PageContent objects with:
  - Page number
  - Text content
  - Section headings
  - Table detection
  - Document name

##### `chunking.py`
- **Purpose**: Split pages into semantically coherent chunks
- **Strategy**: 
  1. Split by paragraphs
  2. Further split large paragraphs by sentences
  3. Maintain 400-700 token chunks
  4. 100-token overlap between chunks
- **Output**: Chunk objects with metadata

##### `vectorstore.py`
- **Purpose**: Create and manage vector embeddings
- **Technology**: 
  - Sentence Transformers (all-MiniLM-L6-v2)
  - FAISS (Facebook AI Similarity Search)
- **Features**:
  - Vector similarity search
  - Query boosting (dosage, safety questions)
  - Save/load index to disk

##### `memory.py`
- **Purpose**: Manage conversation history
- **Strategy**: Sliding window (last 5 message pairs)
- **Storage**: In-memory dictionary (session_id → messages)
- **Features**: Per-session isolation

##### `llm_client.py`
- **Purpose**: Interface with LM Studio
- **Technology**: OpenAI-compatible API
- **Parameters**:
  - Temperature: 0.2 (low creativity)
  - Max tokens: 512
  - Top-p: 0.9

##### `retrieval.py`
- **Purpose**: Orchestrate complete RAG pipeline
- **Flow**:
  1. Receive user query
  2. Retrieve top-K similar chunks
  3. Filter by similarity threshold
  4. Format prompt with context + history
  5. Call LLM
  6. Append citations
  7. Store in memory

##### `prompts.py`
- **Purpose**: Define system and user prompts
- **Key Instructions**:
  - Answer ONLY from context
  - No prior knowledge
  - No guessing
  - Mandatory citations
  - Exact terminology

### 3. LM Studio (Local LLM)

#### Model Specifications
- **Model**: Mistral-7B-Instruct-v0.2
- **Quantization**: Q4_K_S (4-bit)
- **Parameters**: 7 billion
- **Size**: ~4.4 GB
- **RAM Usage**: ~6-8 GB

#### Inference Settings
- **Context Window**: 8192 tokens
- **Temperature**: 0.2 (override-able)
- **Top-P**: 0.9
- **Repeat Penalty**: 1.1

#### API Compatibility
- OpenAI-compatible endpoint
- `/v1/chat/completions` format
- Streaming support (not used)

## Data Flow

### Upload Flow
```
1. User uploads PDF → Frontend
2. Frontend sends file → Backend /upload
3. Backend:
   a. Save to uploads/
   b. Extract pages (PyMuPDF)
   c. Chunk text
   d. Generate embeddings (Sentence Transformers)
   e. Build FAISS index
   f. Save vector store
   g. Return document_id + stats
4. Frontend displays success + stats
```

### Query Flow
```
1. User asks question → Frontend
2. Frontend sends {question, session_id, document_id} → Backend /chat
3. Backend:
   a. Get vector store for document_id
   b. Query vector store (top-K similar chunks)
   c. Apply boosting (dosage/safety questions)
   d. Filter by similarity threshold
   e. Get conversation history (session_id)
   f. Build prompt:
      - System prompt (rules)
      - Retrieved chunks (context)
      - Conversation history
      - User question
   g. Call LM Studio API
   h. Receive answer
   i. Check/append citations
   j. Store in memory (user question + answer)
   k. Return {answer, sources, timestamp}
4. Frontend displays answer with highlighted citations
```

## RAG Pipeline Details

### Retrieval Stage

#### Vector Search
1. Convert user query to embedding (384-dimensional)
2. FAISS searches for L2 nearest neighbors
3. Returns top-K chunks with distances
4. Convert distances to similarity scores

#### Boosting Logic
```python
if "dosage" in query:
    boost *= 1.5 if "dosage" in section
    boost *= 1.3 if has_table

if "warning" in query:
    boost *= 1.5 if "warning" in section
    
if "boxed" in query:
    boost *= 2.0 if "boxed" in section
```

#### Filtering
- Remove chunks with similarity < threshold (0.3)
- Sort by boosted similarity (descending)
- Keep top-K (typically 5)

### Generation Stage

#### Prompt Construction
```
System Prompt: [Rules and constraints]

Extracted Context:
[Chunk 1 - Page X - Section Y]
{text}

[Chunk 2 - Page X - Section Y]
{text}

...

Conversation History:
USER: {previous question}
ASSISTANT: {previous answer}
...

User Question:
{current question}

Answer using ONLY the extracted context above.
```

#### LLM Generation
- LM Studio processes prompt
- Generates answer (max 512 tokens)
- Respects system prompt constraints
- Includes citations (if instructed)

#### Post-Processing
- Extract page numbers from chunks
- Format citation string: "(Page X)" or "(Pages X, Y, and Z)"
- Append if not present in answer
- Validate answer has content

### Memory Stage
- Store user question in session history
- Store assistant answer in session history
- Trim to last 5 message pairs (10 messages)
- Future queries include this history

## Security & Safety

### Healthcare Safety
1. **Mandatory Disclaimer**: Always visible in UI
2. **No Medical Advice**: System prompt explicitly forbids
3. **No Extrapolation**: Only uses provided context
4. **Transparency**: All answers cite sources
5. **Audit Trail**: Conversation history stored

### Data Privacy
1. **Local Processing**: All data stays on-premise
2. **No Cloud APIs**: LLM runs locally (LM Studio)
3. **Session Isolation**: Conversations are session-specific
4. **No Persistence**: Data cleared on restart (configurable)

### Input Validation
1. **File Type**: Only PDF allowed
2. **File Size**: Configurable limit (default 50MB)
3. **Content Validation**: PyMuPDF checks PDF structure
4. **Query Sanitization**: FastAPI request validation

### Error Handling
1. **Graceful Failures**: Never crash, always return response
2. **Error Messages**: User-friendly, non-technical
3. **Logging**: Backend logs all errors for debugging
4. **Fallbacks**: If LLM fails, return "not available" message

## Performance Characteristics

### Latency Breakdown
- **PDF Upload**: 30-60s (80-page document)
  - Extraction: 5-10s
  - Chunking: 2-5s
  - Embedding: 15-30s
  - Indexing: 2-5s
  
- **Query Response**: 3-8s
  - Vector search: 0.1-0.5s
  - Prompt building: 0.1s
  - LLM inference: 2-7s
  - Post-processing: 0.1s

### Resource Usage
- **CPU**: Moderate during indexing, low during queries
- **RAM**: 
  - Backend: 2-4 GB
  - LM Studio: 6-8 GB
  - Total: 8-12 GB
- **Disk**:
  - Model: 4.4 GB
  - Vector stores: ~50 MB per document
  - PDFs: Original file size

### Scalability
- **Documents**: Tested with 1-10 documents
- **Concurrent Users**: Single-user design (expandable)
- **Query Rate**: ~10 queries/minute per user
- **Storage**: Linear with document count

## Extension Points

### Adding New Features

#### Multi-Document Search
```python
# In vectorstore.py
class MultiDocumentStore:
    def __init__(self):
        self.stores = {}  # doc_id → VectorStore
    
    def search_all(self, query):
        results = []
        for doc_id, store in self.stores.items():
            results.extend(store.search(query))
        return sorted(results, key=lambda x: x['similarity'])
```

#### Export Conversation
```python
# In main.py
@app.get("/export/{session_id}")
async def export_conversation(session_id: str):
    history = memory.get_history(session_id)
    pdf = generate_pdf(history)  # Use ReportLab
    return FileResponse(pdf)
```

#### Advanced Analytics
```python
# In retrieval.py
class RAGRetriever:
    def __init__(self):
        self.analytics = {
            'queries': 0,
            'avg_latency': 0,
            'sources_used': []
        }
```

### Integration Options

#### Database Backend
```python
# Replace in-memory storage with SQLite/PostgreSQL
from sqlalchemy import create_engine

engine = create_engine('sqlite:///chatbot.db')
```

#### Authentication
```python
# Add JWT authentication
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/chat")
async def chat(request: ChatRequest, 
               credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Verify token
    pass
```

#### Caching
```python
# Add Redis caching for frequent queries
import redis

cache = redis.Redis(host='localhost', port=6379)

def cached_query(query):
    if cache.exists(query):
        return cache.get(query)
    # ... normal retrieval
    cache.set(query, result, ex=3600)  # 1 hour
```

## Monitoring & Debugging

### Logging
```python
# In main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics to Track
- Query latency (p50, p95, p99)
- LLM inference time
- Vector search time
- Error rates
- Documents processed
- Active sessions

### Debugging Tips
1. **Check logs**: Backend logs show full pipeline
2. **Test components**: Each module has `__main__` test
3. **Verify embeddings**: Check vector store contents
4. **Inspect prompts**: Log full prompt sent to LLM
5. **Validate PDFs**: Test extraction with test script

---

**This architecture documentation provides the foundation for understanding, extending, and maintaining the Drug Information Chatbot system.**
