# 🚀 Quick Start Guide

## Prerequisites Checklist
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed  
- [ ] LM Studio downloaded
- [ ] Mistral-7B-Instruct model downloaded in LM Studio

## 5-Minute Setup

### 1. Install Dependencies (First Time Only)
```powershell
# Run setup script
.\setup.bat

# Or manually:
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

cd ..\frontend
npm install
```

### 2. Start LM Studio
1. Open LM Studio
2. Load: Mistral-7B-Instruct-v0.2
3. Click "Start Server" → localhost:1234

### 3. Start Backend
```powershell
.\start_backend.bat
# Wait for "Application startup complete"
```

### 4. Start Frontend
```powershell
.\start_frontend.bat
# Opens browser at http://localhost:3000
```

### 5. Use the App
1. Upload `rinvoq_pi.pdf` (or any FDA PI PDF)
2. Wait ~30-60 seconds for processing
3. Ask questions!

## Quick Test

### Test Questions
```
"What is the recommended dosage for ulcerative colitis?"
"What are the boxed warnings?"
"Is RINVOQ contraindicated in hepatic impairment?"
```

## Expected Results
- ✅ Answer includes page citation
- ✅ Dosages highlighted in blue
- ✅ Warnings highlighted in red
- ✅ Response time: 3-8 seconds

## Common Issues

| Problem | Solution |
|---------|----------|
| LM Studio disconnected | Start LM Studio server |
| Backend won't start | Activate venv, check Python |
| Frontend errors | `npm install`, restart |
| Slow responses | Close other apps, free RAM |
| PDF upload fails | Check file type, not encrypted |

## Key Commands

```powershell
# Setup
.\setup.bat

# Start
.\start_backend.bat    # Terminal 1
.\start_frontend.bat   # Terminal 2

# Test
cd backend
.\venv\Scripts\Activate.ps1
python quickstart.py   # Process rinvoq_pi.pdf
python tests\test_backend.py  # Run tests
```

## Project Structure
```
MedQueryAI/
├── backend/           # Python FastAPI server
│   ├── main.py       # API endpoints
│   ├── ingest_pdf.py # PDF extraction
│   ├── vectorstore.py # FAISS search
│   └── retrieval.py  # RAG pipeline
├── frontend/         # React app
│   └── src/
│       ├── App.jsx
│       └── components/
└── rinvoq_pi.pdf     # Example PDF
```

## URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **LM Studio**: http://localhost:1234

## Key Features
- ✅ Zero hallucination (answers ONLY from PDF)
- ✅ Mandatory page citations
- ✅ Section-aware chunking
- ✅ Local LLM (privacy-first)
- ✅ Conversation memory
- ✅ Healthcare-safe

## Next Steps
1. Read: `USER_GUIDE.md` for detailed usage
2. Read: `ARCHITECTURE.md` for technical details
3. Read: `DEPLOYMENT.md` for troubleshooting
4. Modify: `backend/config.py` to tune parameters

## Getting Help
- Check terminal output for errors
- Review logs in backend terminal
- Open browser console (F12) for frontend errors
- See `DEPLOYMENT.md` troubleshooting section

---

**You're ready to go! 🎉**

Upload a PDF and start asking questions about prescribing information.
