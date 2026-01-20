# 🤝 Contributing to Drug Information Chatbot

Thank you for your interest in contributing! This project is designed to be a healthcare-safe, regulatory-grade tool, so we have specific guidelines to maintain quality and safety.

## Code of Conduct

### Our Standards

**✅ DO:**
- Maintain healthcare safety as top priority
- Preserve zero-hallucination architecture
- Keep mandatory citations
- Write clear, documented code
- Test thoroughly before submitting
- Follow existing code style

**❌ DON'T:**
- Add features that provide medical advice
- Remove safety constraints
- Skip citation requirements
- Break existing functionality
- Submit untested code

## How to Contribute

### Reporting Bugs

**Before submitting:**
1. Check existing issues
2. Test with latest version
3. Reproduce the bug consistently

**Bug Report Format:**
```markdown
**Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: Windows 10/11
- Python version: 3.10
- Node version: 18.x
- LM Studio version: x.x.x

**Logs:**
Paste relevant error logs

**Screenshots:**
If applicable
```

### Suggesting Features

**Feature Request Format:**
```markdown
**Feature Description:**
Clear description of the feature

**Use Case:**
Why is this needed?

**Healthcare Safety:**
How does this maintain safety standards?

**Implementation Ideas:**
Optional technical suggestions

**Alternatives Considered:**
Other approaches you've thought about
```

### Pull Requests

#### Before You Start

1. **Open an issue** to discuss major changes
2. **Check existing PRs** to avoid duplicates
3. **Review architecture** (ARCHITECTURE.md)
4. **Understand safety constraints** (README.md)

#### Development Process

1. **Fork the repository**
2. **Create a branch**: `feature/your-feature-name` or `fix/bug-description`
3. **Make your changes**
4. **Test thoroughly** (see Testing section)
5. **Update documentation**
6. **Submit pull request**

#### PR Guidelines

**Title Format:**
- `Feature: Add multi-document support`
- `Fix: Resolve PDF upload timeout`
- `Docs: Update deployment guide`

**Description Template:**
```markdown
## Description
Clear description of changes

## Motivation
Why is this change needed?

## Changes Made
- Change 1
- Change 2
- Change 3

## Healthcare Safety Impact
How does this affect safety guarantees?

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] No regression issues

## Documentation
- [ ] Code comments added
- [ ] README.md updated (if needed)
- [ ] ARCHITECTURE.md updated (if needed)

## Screenshots
If applicable
```

## Development Setup

### Environment Setup

```powershell
# Clone your fork
git clone https://github.com/YOUR_USERNAME/MedQueryAI.git
cd MedQueryAI

# Setup backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r tests\requirements-test.txt

# Setup frontend
cd ..\frontend
npm install

# Setup pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Code Style

#### Python (Backend)

**Follow PEP 8:**
```python
# Good
def process_pdf(pdf_path: str) -> List[PageContent]:
    """
    Process PDF and extract pages
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        List of PageContent objects
    """
    pages = ingest_pdf(pdf_path)
    return pages


# Bad
def processPDF(path):
    pages=ingest_pdf(path)
    return pages
```

**Type Hints:**
- Use type hints for all function signatures
- Use `typing` module for complex types

**Docstrings:**
- Use Google-style docstrings
- Document all parameters and return values

**Imports:**
```python
# Standard library
import os
import sys

# Third-party
import numpy as np
from fastapi import FastAPI

# Local
from ingest_pdf import ingest_pdf
from config import CHUNK_SIZE
```

#### JavaScript (Frontend)

**Follow Modern React Patterns:**
```javascript
// Good - Functional components with hooks
const ChatPanel = ({ documentId, sessionId }) => {
  const [messages, setMessages] = useState([]);
  
  return (
    <div className="chat-panel">
      {messages.map((msg, i) => (
        <ChatMessage key={i} message={msg} />
      ))}
    </div>
  );
};


// Bad - Class components, inline styles
class ChatPanel extends React.Component {
  render() {
    return <div style={{padding: '20px'}}>...</div>;
  }
}
```

**Naming:**
- Components: PascalCase (`ChatPanel`)
- Functions: camelCase (`sendMessage`)
- Constants: UPPER_SNAKE_CASE (`API_BASE_URL`)

### Testing

#### Backend Tests

**Unit Tests:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python tests\test_backend.py
```

**API Tests:**
```powershell
# Backend must be running
python tests\test_api.py
```

**Writing Tests:**
```python
import unittest
from your_module import your_function

class TestYourFeature(unittest.TestCase):
    def setUp(self):
        """Setup test fixtures"""
        pass
    
    def test_your_feature(self):
        """Test description"""
        result = your_function()
        self.assertIsNotNone(result)
    
    def test_error_handling(self):
        """Test error cases"""
        with self.assertRaises(ValueError):
            your_function(invalid_input)
```

#### Frontend Tests

**Manual Testing:**
1. Start backend and frontend
2. Upload test PDF
3. Try various queries
4. Check console for errors
5. Test edge cases

### Documentation

#### Code Documentation

**Python:**
```python
def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict]:
    """
    Retrieve relevant context chunks for a query
    
    This method performs vector similarity search and applies
    query-specific boosting to improve relevance.
    
    Args:
        query: User query string
        top_k: Number of chunks to retrieve (default: 5)
    
    Returns:
        List of chunk dictionaries with 'text', 'metadata', 
        'similarity' keys
    
    Raises:
        ValueError: If index not built
    
    Example:
        >>> chunks = retriever.retrieve_context("dosage", top_k=3)
        >>> print(chunks[0]['metadata']['page'])
        9
    """
```

**React:**
```javascript
/**
 * Send a chat message and update state
 * 
 * @param {string} message - The user's message
 * @returns {Promise<void>}
 * @throws {Error} If API call fails
 */
const sendMessage = async (message) => {
  // Implementation
};
```

#### File Headers

**Python:**
```python
"""
Module Name - Brief description

Detailed description of what this module does.

Classes:
    ClassName: Description
    
Functions:
    function_name: Description
"""
```

**JavaScript:**
```javascript
/**
 * Component Name - Brief description
 * 
 * Detailed description of what this component does.
 * 
 * @component
 */
```

### Healthcare Safety Requirements

#### Safety-Critical Changes

Changes to these components require extra scrutiny:
- `prompts.py` - System prompts
- `retrieval.py` - RAG pipeline
- `llm_client.py` - LLM interface

**Safety Checklist:**
- [ ] Maintains zero-hallucination design
- [ ] Preserves citation requirements
- [ ] No medical advice added
- [ ] No external knowledge sources
- [ ] Error handling maintains safety
- [ ] Documentation updated

#### Testing Safety Features

```python
def test_citation_required(self):
    """Ensure all answers have citations"""
    answer = retriever.answer_question("test", "session")
    self.assertIn("(Page", answer['answer'])

def test_no_external_knowledge(self):
    """Ensure system doesn't use external knowledge"""
    answer = retriever.answer_question(
        "What is aspirin?", "session"
    )
    self.assertIn("not available", answer['answer'])
```

## Areas for Contribution

### High Priority

1. **Multi-document support**
   - Search across multiple PDFs
   - Document selection in UI

2. **Export functionality**
   - Export conversations to PDF
   - Export citations list

3. **Improved error messages**
   - User-friendly error text
   - Troubleshooting hints

### Medium Priority

4. **Admin dashboard**
   - Usage statistics
   - System monitoring
   - Document management

5. **Advanced search**
   - Filter by section
   - Date range filtering
   - Complex queries

6. **Performance optimizations**
   - Caching layer
   - Faster indexing
   - GPU acceleration

### Nice to Have

7. **Mobile UI**
   - Responsive design
   - Touch-optimized

8. **Dark mode**
   - Theme switcher
   - Persistent preference

9. **Accessibility**
   - Screen reader support
   - Keyboard navigation
   - WCAG compliance

## Review Process

### What We Look For

**Code Quality:**
- ✅ Clear, readable code
- ✅ Proper error handling
- ✅ Type hints (Python)
- ✅ No code smells

**Testing:**
- ✅ Tests pass
- ✅ New tests for new features
- ✅ Edge cases covered

**Documentation:**
- ✅ Code comments
- ✅ Updated README/docs
- ✅ Clear commit messages

**Safety:**
- ✅ No medical advice
- ✅ Citations preserved
- ✅ No hallucinations introduced

### Review Timeline

- Small fixes: 1-2 days
- New features: 3-7 days
- Major changes: 1-2 weeks

## Questions?

- **General questions**: Open a discussion issue
- **Bug reports**: Use bug report template
- **Feature requests**: Use feature request template
- **Security issues**: Email directly (don't open public issue)

## Attribution

Contributors will be acknowledged in:
- README.md Contributors section
- Release notes
- Commit history

Thank you for helping make this project better while maintaining healthcare safety! 🎉
