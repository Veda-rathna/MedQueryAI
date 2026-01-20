"""
Test Suite for Backend Components
"""
import unittest
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ingest_pdf import ingest_pdf, PDFIngestor
from chunking import chunk_pages, SmartChunker
from vectorstore import VectorStore
from memory import ConversationMemory

class TestPDFIngestion(unittest.TestCase):
    """Test PDF ingestion functionality"""
    
    def setUp(self):
        self.test_pdf = os.path.join(
            os.path.dirname(__file__), '..', '..', 'rinvoq_pi.pdf'
        )
    
    def test_pdf_exists(self):
        """Test that the PDF file exists"""
        self.assertTrue(os.path.exists(self.test_pdf))
    
    def test_pdf_ingestion(self):
        """Test basic PDF ingestion"""
        pages = ingest_pdf(self.test_pdf)
        self.assertGreater(len(pages), 0)
        self.assertIsNotNone(pages[0].text)
        self.assertEqual(pages[0].page_number, 1)
    
    def test_section_extraction(self):
        """Test that sections are extracted"""
        pages = ingest_pdf(self.test_pdf)
        has_sections = any(len(page.sections) > 0 for page in pages)
        self.assertTrue(has_sections)


class TestChunking(unittest.TestCase):
    """Test chunking functionality"""
    
    def setUp(self):
        self.test_pdf = os.path.join(
            os.path.dirname(__file__), '..', '..', 'rinvoq_pi.pdf'
        )
        self.pages = ingest_pdf(self.test_pdf)
    
    def test_chunking(self):
        """Test that pages are chunked correctly"""
        chunks = chunk_pages(self.pages)
        self.assertGreater(len(chunks), 0)
        
        # Check chunk structure
        first_chunk = chunks[0]
        self.assertIsNotNone(first_chunk.text)
        self.assertIsNotNone(first_chunk.metadata)
        self.assertIn('page', first_chunk.metadata)
        self.assertIn('section', first_chunk.metadata)
    
    def test_chunk_size(self):
        """Test that chunks are reasonably sized"""
        chunker = SmartChunker(chunk_size=600, overlap=100)
        chunks = chunker.create_chunks_from_pages(self.pages)
        
        for chunk in chunks:
            tokens = chunker.estimate_tokens(chunk.text)
            # Allow some variance
            self.assertLess(tokens, 1000)


class TestVectorStore(unittest.TestCase):
    """Test vector store functionality"""
    
    def setUp(self):
        self.test_pdf = os.path.join(
            os.path.dirname(__file__), '..', '..', 'rinvoq_pi.pdf'
        )
        self.pages = ingest_pdf(self.test_pdf)
        self.chunks = chunk_pages(self.pages)
    
    def test_vector_store_creation(self):
        """Test vector store creation"""
        store = VectorStore()
        store.build_index(self.chunks)
        
        self.assertIsNotNone(store.index)
        self.assertEqual(store.index.ntotal, len(self.chunks))
    
    def test_search(self):
        """Test vector search"""
        store = VectorStore()
        store.build_index(self.chunks)
        
        results = store.search("dosage", top_k=5)
        
        self.assertEqual(len(results), 5)
        self.assertIn('text', results[0])
        self.assertIn('metadata', results[0])
        self.assertIn('similarity', results[0])


class TestMemory(unittest.TestCase):
    """Test conversation memory functionality"""
    
    def test_memory_add_message(self):
        """Test adding messages to memory"""
        memory = ConversationMemory(max_history=5)
        session_id = "test-session"
        
        memory.add_message(session_id, "user", "What is the dosage?")
        memory.add_message(session_id, "assistant", "15 mg once daily.")
        
        history = memory.get_history(session_id)
        self.assertEqual(len(history), 2)
    
    def test_memory_sliding_window(self):
        """Test that memory maintains sliding window"""
        memory = ConversationMemory(max_history=2)
        session_id = "test-session"
        
        # Add more than max_history pairs
        for i in range(10):
            memory.add_message(session_id, "user", f"Question {i}")
            memory.add_message(session_id, "assistant", f"Answer {i}")
        
        history = memory.get_history(session_id)
        # Should keep only last 2 pairs (4 messages)
        self.assertEqual(len(history), 4)
    
    def test_clear_session(self):
        """Test clearing session history"""
        memory = ConversationMemory()
        session_id = "test-session"
        
        memory.add_message(session_id, "user", "Test")
        memory.clear_session(session_id)
        
        history = memory.get_history(session_id)
        self.assertEqual(len(history), 0)


def run_tests():
    """Run all tests"""
    print("Running Drug Information Chatbot Tests...")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestPDFIngestion))
    suite.addTests(loader.loadTestsFromTestCase(TestChunking))
    suite.addTests(loader.loadTestsFromTestCase(TestVectorStore))
    suite.addTests(loader.loadTestsFromTestCase(TestMemory))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
