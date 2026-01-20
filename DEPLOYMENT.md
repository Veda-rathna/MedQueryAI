# 🚀 Deployment & Production Guide

## Pre-Deployment Checklist

### System Requirements
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] LM Studio installed and configured
- [ ] 16GB RAM available
- [ ] 10GB disk space available

### LM Studio Configuration
- [ ] Model downloaded: `TheBloke/Mistral-7B-Instruct-v0.2-GGUF (Q4_K_S)`
- [ ] Server running on `localhost:1234`
- [ ] API endpoint: `http://localhost:1234/v1/chat/completions`
- [ ] Test endpoint responds: `curl http://localhost:1234/v1/models`

### Backend Configuration
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `config.py` reviewed and configured
- [ ] Upload directories created
- [ ] Vector store directory created

### Frontend Configuration
- [ ] Node modules installed
- [ ] `vite.config.js` proxy configured
- [ ] Tailwind CSS compiled
- [ ] API base URL configured

## Quick Start (Development)

### 1. Setup (First Time Only)
```powershell
# Run the setup script
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
2. Load model: Mistral-7B-Instruct-v0.2
3. Start server (localhost:1234)
4. Verify server is running

### 3. Start Backend
```powershell
# Option 1: Use batch file
.\start_backend.bat

# Option 2: Manual
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

Backend will be available at: `http://localhost:8000`

### 4. Start Frontend
```powershell
# Option 1: Use batch file
.\start_frontend.bat

# Option 2: Manual
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## Testing

### Quick Test
```powershell
# Test backend components
cd backend
.\venv\Scripts\Activate.ps1
python quickstart.py
```

### Full Test Suite
```powershell
# Run unit tests
.\run_tests.bat

# Or manually
cd backend
.\venv\Scripts\Activate.ps1
python tests\test_backend.py

# Test API (requires backend running)
python tests\test_api.py
```

## Configuration

### Backend Configuration (`backend/config.py`)

#### LLM Settings
```python
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
LLM_TEMPERATURE = 0.2      # Lower = more deterministic
LLM_MAX_TOKENS = 512       # Maximum response length
LLM_TOP_P = 0.9            # Nucleus sampling
```

**Tuning Tips:**
- **Temperature**: 0.1-0.3 for factual answers, 0.4-0.7 for creative
- **Max Tokens**: 256 for short answers, 512-1024 for detailed
- **Top-P**: 0.9 is good default, lower (0.8) for more focused

#### Chunking Settings
```python
CHUNK_SIZE = 600           # Tokens per chunk
CHUNK_OVERLAP = 100        # Overlap between chunks
```

**Tuning Tips:**
- **Larger chunks** (800-1000): Better context, slower search
- **Smaller chunks** (400-600): Faster search, less context
- **Overlap**: 100-200 tokens ensures continuity

#### Retrieval Settings
```python
TOP_K_CHUNKS = 5           # Number of chunks to retrieve
SIMILARITY_THRESHOLD = 0.3 # Minimum similarity score
```

**Tuning Tips:**
- **TOP_K**: 3-5 for focused answers, 7-10 for comprehensive
- **Threshold**: 0.2-0.4 (lower = more results, higher = stricter)

### Frontend Configuration (`frontend/vite.config.js`)

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

## Troubleshooting

### Issue: LM Studio Connection Failed

**Symptoms:**
- Health check shows "LM Studio Disconnected"
- Chat requests fail with connection errors
- Backend logs show connection refused

**Solutions:**

1. **Check LM Studio is running:**
   ```powershell
   curl http://localhost:1234/v1/models
   ```
   Should return JSON with model info.

2. **Verify port 1234 is not in use:**
   ```powershell
   netstat -ano | findstr :1234
   ```

3. **Check firewall settings:**
   - Allow LM Studio through Windows Firewall
   - Allow localhost connections

4. **Restart LM Studio:**
   - Close LM Studio completely
   - Restart and load model
   - Start server again

5. **Check model is loaded:**
   - LM Studio UI should show model loaded
   - Server status should be "Running"

### Issue: PDF Upload Fails

**Symptoms:**
- Upload hangs or times out
- Error: "Failed to process PDF"
- Backend shows extraction errors

**Solutions:**

1. **Check PDF is valid:**
   - Not encrypted
   - Not password protected
   - Contains extractable text (not scanned images)

2. **Verify PyMuPDF is installed:**
   ```powershell
   pip install --upgrade pymupdf
   ```

3. **Check file size:**
   - PDFs > 50MB may timeout
   - Increase timeout in FastAPI config

4. **Check disk space:**
   - Ensure uploads/ directory has space
   - Check vector_stores/ has space

5. **Check permissions:**
   ```powershell
   # Verify directories exist and are writable
   ls backend/uploads
   ls backend/vector_stores
   ```

### Issue: Slow Response Times

**Symptoms:**
- Queries take > 30 seconds
- Frontend shows loading for long time
- Backend CPU usage high

**Solutions:**

1. **Reduce chunk retrieval:**
   ```python
   # In config.py
   TOP_K_CHUNKS = 3  # Reduce from 5
   ```

2. **Use smaller/faster model:**
   - Try Q3_K_S or Q2_K quantization
   - Faster inference, slightly lower quality

3. **Reduce max tokens:**
   ```python
   # In config.py
   LLM_MAX_TOKENS = 256  # Reduce from 512
   ```

4. **Check system resources:**
   - Close other applications
   - Ensure 8GB+ RAM available
   - Check CPU isn't throttling

5. **Optimize vector search:**
   ```python
   # In vectorstore.py, use faster index
   self.index = faiss.IndexFlatIP(self.dimension)  # Inner product
   ```

### Issue: Incorrect or Hallucinated Answers

**Symptoms:**
- Answers don't match PDF content
- No citations provided
- Answers seem "made up"

**Solutions:**

1. **Lower temperature:**
   ```python
   # In config.py
   LLM_TEMPERATURE = 0.1  # More deterministic
   ```

2. **Increase similarity threshold:**
   ```python
   # In config.py
   SIMILARITY_THRESHOLD = 0.4  # Stricter matching
   ```

3. **Check system prompt is enforced:**
   - Verify prompts.py has strict instructions
   - Check LLM is respecting system prompt

4. **Retrieve more context:**
   ```python
   # In config.py
   TOP_K_CHUNKS = 7  # More context
   ```

5. **Re-process PDF:**
   - Delete from uploads/ and vector_stores/
   - Re-upload to rebuild index

### Issue: Frontend Build Errors

**Symptoms:**
- `npm run dev` fails
- Vite compilation errors
- Module not found errors

**Solutions:**

1. **Clean install:**
   ```powershell
   cd frontend
   rm -rf node_modules
   rm package-lock.json
   npm install
   ```

2. **Check Node version:**
   ```powershell
   node --version  # Should be 16+
   npm --version
   ```

3. **Clear Vite cache:**
   ```powershell
   rm -rf .vite
   npm run dev
   ```

4. **Check for port conflicts:**
   ```powershell
   netstat -ano | findstr :3000
   ```

### Issue: Memory Errors

**Symptoms:**
- Backend crashes with MemoryError
- System becomes unresponsive
- LM Studio crashes

**Solutions:**

1. **Use smaller model:**
   - Q4_K_S → Q3_K_S (less RAM)
   - Consider 7B → 3B parameter model

2. **Reduce batch processing:**
   ```python
   # In vectorstore.py
   # Process embeddings in smaller batches
   ```

3. **Close other applications:**
   - Free up system RAM
   - Close browser tabs

4. **Increase system swap:**
   - Windows: Increase virtual memory
   - Allows overflow to disk

### Issue: Conversation History Not Working

**Symptoms:**
- Follow-up questions don't have context
- "What did you say earlier?" doesn't work
- Each query seems independent

**Solutions:**

1. **Check session ID:**
   - Frontend should generate consistent session_id
   - Verify it's passed in API calls

2. **Check memory module:**
   ```python
   # In memory.py
   print(f"Session {session_id} has {len(history)} messages")
   ```

3. **Verify history limit:**
   ```python
   # In config.py
   MAX_HISTORY_MESSAGES = 5  # Increase if needed
   ```

4. **Check browser storage:**
   - Session ID stored in component state
   - Refreshing page creates new session

## Performance Optimization

### Backend Optimizations

1. **Use GPU acceleration (if available):**
   ```python
   # In vectorstore.py
   import faiss
   res = faiss.StandardGpuResources()
   self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
   ```

2. **Cache embeddings:**
   - Save embeddings to disk
   - Reuse for similar queries

3. **Async processing:**
   - Make retrieval async
   - Parallel chunk processing

4. **Database for metadata:**
   - Use SQLite for chunk metadata
   - Faster than pickle for large datasets

### Frontend Optimizations

1. **Lazy load components:**
   ```javascript
   const ChatPanel = lazy(() => import('./components/ChatPanel'));
   ```

2. **Debounce typing:**
   - Don't send query on every keystroke
   - Wait for user to stop typing

3. **Virtual scrolling:**
   - For long conversation histories
   - Render only visible messages

4. **Code splitting:**
   - Separate chunks for different routes
   - Faster initial load

## Production Deployment

### Security Considerations

1. **API Authentication:**
   - Add JWT tokens
   - Implement rate limiting
   - CORS configuration

2. **File Upload Validation:**
   - Virus scanning
   - Size limits enforced
   - Type validation

3. **Environment Variables:**
   ```python
   # Use .env file
   from dotenv import load_dotenv
   load_dotenv()
   
   LM_STUDIO_BASE_URL = os.getenv('LM_STUDIO_URL')
   ```

4. **HTTPS:**
   - Use reverse proxy (nginx)
   - SSL certificates
   - Secure websockets

### Scalability

1. **Multiple Workers:**
   ```powershell
   uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
   ```

2. **Load Balancing:**
   - Multiple backend instances
   - nginx load balancer

3. **Separate Services:**
   - PDF processing service
   - LLM inference service
   - API gateway

4. **Caching:**
   - Redis for session storage
   - Cache frequent queries

### Monitoring

1. **Logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   ```

2. **Metrics:**
   - Response times
   - Query success rate
   - Error rates

3. **Health Checks:**
   - Automated health monitoring
   - Alert on failures

## Backup & Recovery

### Backup Strategy

1. **Vector Stores:**
   ```powershell
   # Backup vector stores
   xcopy backend\vector_stores backup\vector_stores /E /I /Y
   ```

2. **Uploaded PDFs:**
   ```powershell
   # Backup uploads
   xcopy backend\uploads backup\uploads /E /I /Y
   ```

3. **Configuration:**
   ```powershell
   # Backup config
   copy backend\config.py backup\config.py
   ```

### Recovery

1. **Restore vector stores:**
   ```powershell
   xcopy backup\vector_stores backend\vector_stores /E /I /Y
   ```

2. **Rebuild if needed:**
   ```powershell
   python backend\quickstart.py
   ```

## Maintenance

### Regular Tasks

1. **Clear old sessions:**
   ```python
   # Add to memory.py
   def cleanup_old_sessions(self, hours=24):
       # Remove sessions older than X hours
   ```

2. **Rotate logs:**
   - Keep last 7 days of logs
   - Archive older logs

3. **Update dependencies:**
   ```powershell
   pip list --outdated
   pip install --upgrade <package>
   ```

4. **Monitor disk usage:**
   - uploads/ directory
   - vector_stores/ directory
   - Clear old documents

### Updates

1. **Model updates:**
   - Download new model version
   - Test with sample queries
   - Update config.py

2. **Dependency updates:**
   - Test in dev environment first
   - Update requirements.txt
   - Document breaking changes

3. **Feature additions:**
   - Follow git workflow
   - Test thoroughly
   - Update documentation

---

**For additional help, see README.md or review code comments.**
