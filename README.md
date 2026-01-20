# 🩺 Drug Information Chatbot

A regulatory-grade chatbot system for FDA prescribing information PDFs, built with Retrieval-Augmented Generation (RAG) architecture and local LLM inference.

## 🎯 Overview

This system extracts, understands, retrieves, and answers questions **strictly from uploaded PDF documents**, preserving section structure, dosage tables, boxed warnings, and page-level citations.

### Key Features

- **Zero Hallucination**: Answers ONLY from provided PDF content
- **Mandatory Citations**: Every answer includes page references
- **Section-Aware**: Preserves FDA document structure (1.4, 2.6, 5.1, etc.)
- **Table Preservation**: Dosage tables remain intact
- **Local LLM**: Privacy-first inference via LM Studio
- **Healthcare-Safe**: Built-in disclaimers and safety guardrails

## 🏗️ Architecture

### Backend (Python + FastAPI)
```
PDF Upload → PyMuPDF Extraction → Smart Chunking → FAISS Vector Store → RAG Pipeline → LM Studio LLM
```

### Frontend (React + Tailwind)
```
Drag & Drop Upload → Chat Interface → Markdown Rendering → Citation Highlighting
```

## 📋 System Requirements

### Backend
- Python 3.8+
- 8GB RAM minimum (16GB recommended)
- LM Studio running locally

### Frontend
- Node.js 16+
- npm or yarn

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
cd d:\Code_wid_pablo\MedQueryAI
```

### 2. Backend Setup

#### Install Python Dependencies
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Configure LM Studio
1. Download [LM Studio](https://lmstudio.ai/)
2. Download model: `TheBloke/Mistral-7B-Instruct-v0.2-GGUF` (Q4_K_S variant)
3. Start LM Studio server on `localhost:1234`
4. Verify it's using the `/v1/chat/completions` endpoint

### 3. Frontend Setup

```powershell
cd ..\frontend
npm install
```

## ▶️ Running the Application

### Start Backend (Terminal 1)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```
Backend runs on: `http://localhost:8000`

### Start Frontend (Terminal 2)
```powershell
cd frontend
npm run dev
```
Frontend runs on: `http://localhost:3000`

### Verify LM Studio
Make sure LM Studio is running and shows:
- Server: `http://localhost:1234`
- Model loaded: Mistral-7B-Instruct-v0.2

## 📖 Usage

### 1. Upload PDF
- Drag & drop an FDA prescribing information PDF (e.g., `rinvoq_pi.pdf`)
- System processes: extracts pages → chunks text → builds vector index
- Wait for "Successfully processed" message

### 2. Ask Questions
Example queries:
- "What is the recommended dosage for ulcerative colitis?"
- "What are the boxed warnings?"
- "Is RINVOQ contraindicated in hepatic impairment?"
- "What are the common adverse reactions?"
- "What should be evaluated before initiating treatment?"

### 3. Review Answers
- Answers include **page citations** (e.g., "Page 9")
- Click citations to see page references
- Dosages, warnings, and contraindications are highlighted
- Conversation history maintained per session

## 🧠 How RAG Prevents Hallucination

### 1. **Strict Context Retrieval**
- User query → Vector search → Top-K most similar chunks
- Chunks contain exact text from PDF with metadata (page, section)

### 2. **System Prompt Enforcement**
```
You must answer ONLY using the provided context.
Do not use prior knowledge.
If information is not present, respond: "This information is not available."
```

### 3. **Temperature = 0.2**
- Low temperature = deterministic, less creative
- Reduces likelihood of fabrication

### 4. **Citation Requirement**
- LLM instructed to cite pages
- Answers without citations are flagged
- Backend appends citations if missing

### 5. **Local LLM = No External Data Leakage**
- All inference happens on your machine
- No data sent to external APIs
- Full control over model behavior

## 🔧 Configuration

### Backend (`backend/config.py`)
```python
# LLM Settings
LLM_TEMPERATURE = 0.2      # Lower = less creative
LLM_MAX_TOKENS = 512       # Answer length limit
LLM_TOP_P = 0.9            # Nucleus sampling

# Chunking
CHUNK_SIZE = 600           # Tokens per chunk
CHUNK_OVERLAP = 100        # Overlap between chunks

# Retrieval
TOP_K_CHUNKS = 5           # Number of chunks to retrieve
SIMILARITY_THRESHOLD = 0.3 # Minimum similarity score
```

### Frontend (`frontend/src/services/api.js`)
```javascript
const API_BASE_URL = '/api';  // Proxied to localhost:8000
```

## 📂 Project Structure

```
MedQueryAI/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── ingest_pdf.py        # PDF extraction (PyMuPDF)
│   ├── chunking.py          # Smart text chunking
│   ├── vectorstore.py       # FAISS vector store
│   ├── retrieval.py         # RAG orchestration
│   ├── llm_client.py        # LM Studio client
│   ├── memory.py            # Conversation history
│   ├── prompts.py           # System/user prompts
│   ├── config.py            # Configuration
│   └── requirements.txt     # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadPanel.jsx   # PDF upload UI
│   │   │   ├── ChatPanel.jsx     # Chat interface
│   │   │   ├── ChatMessage.jsx   # Message bubble
│   │   │   └── Disclaimer.jsx    # Safety disclaimer
│   │   ├── services/
│   │   │   └── api.js            # Backend API calls
│   │   ├── App.jsx               # Main app component
│   │   └── main.jsx              # React entry point
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── rinvoq_pi.pdf            # Example FDA document
└── README.md
```

## 🧪 Testing

### Test PDF Ingestion
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python ingest_pdf.py ..\rinvoq_pi.pdf
```

### Test Chunking
```powershell
python chunking.py ..\rinvoq_pi.pdf
```

### Test Vector Store
```powershell
python vectorstore.py ..\rinvoq_pi.pdf
```

### Test LM Studio Connection
```powershell
python llm_client.py
```

### Test Complete Pipeline
```powershell
python retrieval.py ..\rinvoq_pi.pdf
```

## 🛡️ Healthcare Safety Features

### 1. **Mandatory Disclaimer**
Displayed prominently in UI:
> "This chatbot provides information directly from official prescribing documents and does not replace professional medical advice."

### 2. **No Medical Judgment**
- System never diagnoses or recommends treatments
- Only retrieves and presents document content
- No extrapolation beyond provided text

### 3. **Transparency**
- All answers cite source pages
- Users can verify information in original PDF
- Clear indication when information is not available

### 4. **Audit Trail**
- Conversation history stored per session
- Can review what was asked and answered
- Supports compliance and verification

## 🚨 Limitations

### What This System Does NOT Do:
❌ Provide medical advice or diagnosis  
❌ Answer questions outside the uploaded PDF  
❌ Interpret or extrapolate beyond document text  
❌ Recommend off-label uses  
❌ Compare drugs or make clinical decisions  

### What This System DOES Do:
✅ Extract exact text from FDA prescribing information  
✅ Answer questions using only document content  
✅ Cite page numbers for all answers  
✅ Preserve structure (sections, tables, warnings)  
✅ Maintain conversation context  

## 🔍 Example Interactions

### Example 1: Dosage Query
**User**: "What is the recommended dosage for ulcerative colitis?"

**Assistant**: "The recommended dosage for ulcerative colitis is 15 mg once daily for induction, followed by 15 mg or 30 mg once daily for maintenance. (Page 9)"

### Example 2: Safety Query
**User**: "What are the boxed warnings?"

**Assistant**: "RINVOQ has the following boxed warnings:
- Serious infections
- Mortality
- Malignancies
- Major adverse cardiovascular events
- Thrombosis
(Pages 1-2)"

### Example 3: Not Available
**User**: "What is the cost of RINVOQ?"

**Assistant**: "This information is not available in the provided prescribing document."

### Example 4: Follow-up Question
**User**: "What did you say earlier about dosage?"

**Assistant**: "I mentioned that the recommended dosage for ulcerative colitis is 15 mg once daily for induction. (Page 9)"

## 🐛 Troubleshooting

### Issue: "LM Studio Connection Failed"
**Solution**: 
1. Make sure LM Studio is running
2. Check server is on `localhost:1234`
3. Verify model is loaded
4. Test endpoint: `http://localhost:1234/v1/models`

### Issue: "Import errors in backend"
**Solution**:
```powershell
pip install --upgrade -r requirements.txt
```

### Issue: "Frontend won't start"
**Solution**:
```powershell
rm -rf node_modules
npm install
```

### Issue: "PDF processing fails"
**Solution**:
- Check PDF is not encrypted
- Ensure PDF is text-based (not scanned images)
- Try re-uploading

### Issue: "Slow responses"
**Solution**:
- Reduce `TOP_K_CHUNKS` in `config.py`
- Use smaller/faster LLM model
- Increase `LLM_MAX_TOKENS` for faster generation

## 📊 Performance Metrics

### Typical Processing Times:
- **PDF Upload & Processing**: 30-60 seconds (80-page document)
- **Query Response**: 3-8 seconds
- **Vector Search**: <1 second
- **LLM Generation**: 2-7 seconds (depends on answer length)

### Memory Usage:
- **Backend**: 2-4 GB
- **LM Studio**: 4-8 GB (model dependent)
- **Frontend**: <100 MB

## 🔄 Future Enhancements

- [ ] Multi-document support
- [ ] Export conversation to PDF
- [ ] Highlight exact quotes in source pages
- [ ] Voice input/output
- [ ] Mobile responsive design
- [ ] Admin dashboard for usage analytics
- [ ] Support for scanned PDFs (OCR)
- [ ] Multi-language support

## 📄 License

This project is for educational and research purposes. When using with actual FDA prescribing information, ensure compliance with applicable regulations and copyright laws.

## 🙏 Acknowledgments

- **PyMuPDF**: PDF text extraction
- **FAISS**: Vector similarity search
- **Sentence Transformers**: Embeddings
- **LM Studio**: Local LLM inference
- **FastAPI**: Backend framework
- **React + Tailwind**: Frontend UI

---

**Built with ❤️ for healthcare safety and regulatory compliance**

For questions or issues, please check the troubleshooting section or review the code comments.
