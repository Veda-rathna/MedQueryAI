# 📘 User Guide - Drug Information Chatbot

## Welcome!

This guide will help you use the Drug Information Chatbot to extract and query information from FDA prescribing information PDFs.

## ⚠️ Important: What This System Does and Does NOT Do

### ✅ What This System DOES:
- Extracts information directly from uploaded FDA prescribing documents
- Answers questions using ONLY the document content
- Provides page citations for all answers
- Preserves structure, dosage tables, and warnings
- Maintains conversation context

### ❌ What This System DOES NOT Do:
- Provide medical advice or diagnosis
- Answer questions outside the uploaded PDF
- Recommend treatments or dosages
- Compare different drugs
- Interpret or extrapolate beyond document text
- Replace consultation with healthcare professionals

## Getting Started

### Step 1: Start the Application

1. **Start LM Studio** (must be done first!)
   - Open LM Studio application
   - Load the Mistral-7B-Instruct model
   - Click "Start Server"
   - Verify it shows "Server running on localhost:1234"

2. **Start the Backend**
   - Double-click `start_backend.bat`
   - Wait for "Application startup complete"
   - Leave this window open

3. **Start the Frontend**
   - Double-click `start_frontend.bat`
   - Wait for "Local: http://localhost:3000"
   - Your browser should open automatically

4. **Open in Browser**
   - If not opened automatically, go to: `http://localhost:3000`

### Step 2: Upload a PDF

1. **Locate the Upload Panel**
   - You'll see a large area labeled "📄 Upload Prescribing Information PDF"

2. **Upload Your PDF**
   - **Option A**: Drag and drop a PDF file onto the upload area
   - **Option B**: Click the upload area to browse for a file

3. **Wait for Processing**
   - You'll see a progress bar
   - Processing takes 30-60 seconds for typical documents
   - Status shows: "Processing PDF... X% complete"

4. **Processing Complete**
   - You'll see a green checkmark ✅
   - Document information displays:
     - Filename
     - Number of pages
     - Number of chunks created

5. **Troubleshooting Upload**
   - **Error: "Only PDF files are allowed"**
     - Make sure file ends in `.pdf`
   - **Error: "Failed to upload PDF"**
     - Check file is not encrypted or password-protected
     - Ensure file is not corrupted
     - Try a different PDF

### Step 3: Ask Questions

1. **Locate the Chat Panel**
   - Below the upload section
   - Shows "💬 Ask Questions"

2. **Choose a Question**
   - **Option A**: Click an example question button
   - **Option B**: Type your own question in the text box

3. **Send Your Question**
   - Click the "Send" button
   - Or press Enter (Shift+Enter for new line)

4. **Wait for Response**
   - You'll see a thinking animation (🤖 with dots)
   - Typical response time: 3-8 seconds

5. **Review the Answer**
   - Answer appears in a chat bubble
   - **Citations**: Blue boxes showing "(Page X)"
   - **Highlights**:
     - **Blue**: Dosages and administration info
     - **Red**: Warnings and risks
     - **Orange**: Contraindications

## Example Questions

### Dosage Questions
```
✓ "What is the recommended dosage for ulcerative colitis?"
✓ "How should RINVOQ be administered?"
✓ "What is the maintenance dose?"
✓ "Are there dosage adjustments for renal impairment?"
```

### Safety Questions
```
✓ "What are the boxed warnings?"
✓ "What are the serious adverse reactions?"
✓ "Is this drug contraindicated in pregnancy?"
✓ "What are the drug interactions?"
```

### Usage Questions
```
✓ "What are the indications for this drug?"
✓ "Who should not take this medication?"
✓ "What should be monitored during treatment?"
✓ "What should patients be told?"
```

### Follow-up Questions
```
✓ "Can you elaborate on that?"
✓ "What did you say about the dosage?"
✓ "Are there any warnings related to that?"
```

## Understanding Responses

### Response Structure

```
Answer Text with information from the document. 
Dosages and warnings are highlighted. (Page 9)
```

**Components:**
1. **Answer Text**: Direct information from the PDF
2. **Highlights**: Color-coded important terms
3. **Citation**: Page reference in blue box

### Citations

**Single Page:**
```
(Page 9)
```

**Multiple Pages:**
```
(Pages 9, 12, and 15)
```

**Why Citations Matter:**
- Verify information in original PDF
- Ensure accuracy
- Meet regulatory requirements
- Build trust

### When Information is Not Available

If the answer isn't in the PDF, you'll see:
```
"This information is not available in the provided 
prescribing document."
```

**This is expected and correct!** The system won't guess or use external knowledge.

## Advanced Features

### Conversation Context

The system remembers your conversation:

**Example:**
```
You: "What is the dosage for ulcerative colitis?"
Bot: "15 mg once daily for induction... (Page 9)"

You: "What about for Crohn's disease?"
Bot: "For Crohn's disease, the dosage is... (Page 10)"

You: "What did you say earlier about UC?"
Bot: "I mentioned that for ulcerative colitis, 
      the dosage is 15 mg once daily... (Page 9)"
```

The system remembers the last 5 question-answer pairs.

### Clear Conversation

To start fresh:
1. Click "Clear Chat" button (top-right of chat panel)
2. Or refresh the browser page (creates new session)

### Multiple Documents

**Current limitation**: One document at a time

**To switch documents:**
1. Upload a new PDF
2. Previous document is replaced
3. Start asking questions about the new document

## Tips for Best Results

### Writing Good Questions

**✅ DO:**
- Be specific: "What is the dosage for ulcerative colitis?"
- Use medical terms from the document
- Ask one thing at a time
- Reference sections: "What does Section 5 say about warnings?"

**❌ DON'T:**
- Be vague: "Tell me about this drug"
- Ask multiple questions: "What's the dosage and are there warnings?"
- Ask for comparisons: "Is this better than Drug X?"
- Ask for medical advice: "Should I take this?"

### Question Examples

**Good Questions:**
```
✓ "What is the mechanism of action?"
✓ "What are the contraindications in hepatic impairment?"
✓ "What monitoring is recommended during treatment?"
```

**Poor Questions:**
```
✗ "Is this a good drug?"
✗ "Should I prescribe this to my patient?"
✗ "How does this compare to other drugs?"
```

### Interpreting Answers

**The system will:**
- Quote directly from the document
- Use exact terminology
- Cite specific pages
- Preserve structure (tables, lists)

**The system will NOT:**
- Paraphrase in simpler terms (preserves medical accuracy)
- Add context from other sources
- Make recommendations
- Provide interpretations

## Troubleshooting

### "LM Studio Disconnected"

**Symptom:** Red indicator in header, queries fail

**Solution:**
1. Check LM Studio is running
2. Verify server is started in LM Studio
3. Restart LM Studio if needed
4. Refresh browser page

### Slow Responses

**Symptom:** Takes > 15 seconds to get answer

**Solutions:**
1. Close other applications (free up RAM)
2. Use a shorter question
3. Wait - first query is always slower
4. Check your computer isn't running other heavy tasks

### No Answer Received

**Symptom:** Query sent, but no response appears

**Solutions:**
1. Check backend terminal for errors
2. Verify LM Studio is responding
3. Try refreshing the page
4. Re-upload the PDF

### Incorrect Answer

**Symptom:** Answer doesn't match PDF content

**Solutions:**
1. Check the cited page in original PDF
2. Try rephrasing your question more specifically
3. Ask for a specific section
4. Report issue if answer is clearly wrong

### Citations Missing

**Symptom:** Answer has no page reference

**Solutions:**
1. This shouldn't happen - report as bug
2. Try asking the question again
3. Ask "What page is that from?"

## Safety Guidelines

### Medical Use

**Remember:**
- This is an INFORMATION RETRIEVAL tool
- It does NOT provide medical advice
- It does NOT replace clinical judgment
- It does NOT interpret findings

**Appropriate Use:**
```
✓ Looking up dosing information
✓ Checking contraindications
✓ Reviewing warnings and precautions
✓ Finding specific sections quickly
```

**Inappropriate Use:**
```
✗ Making treatment decisions
✗ Diagnosing conditions
✗ Determining drug suitability
✗ Advising patients
```

### Verification

**Always:**
1. ✅ Verify information in original PDF
2. ✅ Check cited pages match
3. ✅ Consult current prescribing information
4. ✅ Follow institutional protocols

**Never:**
1. ❌ Rely solely on chatbot without verification
2. ❌ Use for patient counseling directly
3. ❌ Substitute for clinical decision-making
4. ❌ Share sensitive patient information

## Keyboard Shortcuts

- **Send Message**: `Enter`
- **New Line**: `Shift + Enter`
- **Clear Chat**: Click "Clear Chat" button
- **Upload PDF**: Click upload area or drag & drop

## System Requirements

**To use this system, you need:**
- Modern web browser (Chrome, Firefox, Edge)
- Internet connection NOT required (runs locally)
- Backend and LM Studio running
- 8GB+ RAM available
- Screen resolution: 1280x720 or higher

## Getting Help

### Check Logs

**Backend Terminal:**
- Shows processing steps
- Displays any errors
- Shows query details

**Browser Console:**
- Press F12 in browser
- Click "Console" tab
- Check for errors (red text)

### Common Issues

1. **PDF won't upload**: Check file type and size
2. **No response**: Check LM Studio connection
3. **Slow response**: Close other applications
4. **Wrong answer**: Rephrase question more specifically

### Report Issues

If you encounter problems:
1. Note the exact error message
2. Check what you were trying to do
3. Check backend terminal for errors
4. Review troubleshooting section in README.md

## Best Practices

### For Healthcare Professionals

1. **Verification First**
   - Always verify critical information
   - Check cited pages in original document
   - Use as a quick reference, not primary source

2. **Specific Queries**
   - Ask about specific sections
   - Use medical terminology
   - One concept per question

3. **Context Awareness**
   - Remember system only knows uploaded document
   - No comparison to other drugs
   - No external guidelines

### For Researchers

1. **Documentation**
   - Citations make it easy to document sources
   - Save conversations for reference
   - Export functionality (if implemented)

2. **Systematic Review**
   - Upload one document at a time
   - Work through sections methodically
   - Keep notes of key findings

### For Regulatory Affairs

1. **Compliance**
   - All answers are traceable to source
   - Citations support audit trail
   - No unauthorized interpretation

2. **Version Control**
   - Note document version being queried
   - Re-upload if prescribing info updated
   - Archive vector stores for records

## Limitations

### What to Expect

**System Strengths:**
- ✅ Fast information retrieval
- ✅ Accurate citations
- ✅ Preserves exact wording
- ✅ Conversation context
- ✅ Highlights key information

**System Limitations:**
- ⚠️ One document at a time
- ⚠️ No cross-document search
- ⚠️ No image/chart interpretation
- ⚠️ No external knowledge
- ⚠️ Limited to English

### When to Use Traditional Search

**Use the chatbot when:**
- Exploring a document
- Need quick answers
- Want conversation flow
- Checking specific facts

**Use PDF search (Ctrl+F) when:**
- Know exact phrase
- Need all occurrences
- Want to scan quickly
- Reviewing tables/charts

## FAQ

**Q: How accurate are the answers?**
A: Answers are extracted directly from the PDF. Accuracy depends on the PDF quality and how well your question matches the content.

**Q: Can I upload multiple PDFs?**
A: Currently, one at a time. Upload a new PDF to replace the current one.

**Q: Is my data private?**
A: Yes! Everything runs locally on your computer. No data is sent to external servers.

**Q: How long are conversations stored?**
A: Conversations are stored in memory while the application runs. They're cleared when you restart the backend.

**Q: Can I export conversations?**
A: Not currently implemented, but can be added. Check ARCHITECTURE.md for extension points.

**Q: Why is the first query slow?**
A: The LLM needs to "warm up". Subsequent queries are faster.

**Q: Can I use this offline?**
A: Yes! Once set up, no internet connection is required.

**Q: What PDF formats are supported?**
A: Text-based PDFs. Scanned PDFs (images) may not work well without OCR.

**Q: How do I update the system?**
A: Pull latest changes from repository, reinstall dependencies, restart backend.

---

**Need more help?** Check the README.md, DEPLOYMENT.md, or ARCHITECTURE.md files for technical details.

**Remember:** This tool is for information retrieval only. Always consult healthcare professionals for medical decisions.
