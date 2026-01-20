"""
Quick Start Script - Process the RINVOQ PDF and test the system
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from ingest_pdf import ingest_pdf
from chunking import chunk_pages
from vectorstore import create_vector_store
from memory import ConversationMemory
from retrieval import create_retriever
import config

def main():
    pdf_path = os.path.join(os.path.dirname(__file__), '..', 'rinvoq_pi.pdf')
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        print("Please place rinvoq_pi.pdf in the project root directory.")
        return
    
    print("🔄 Processing RINVOQ Prescribing Information...")
    print("=" * 60)
    
    # Step 1: Ingest PDF
    print("\n1️⃣  Ingesting PDF...")
    pages = ingest_pdf(pdf_path)
    print(f"✓ Extracted {len(pages)} pages")
    
    # Step 2: Chunk
    print("\n2️⃣  Chunking text...")
    chunks = chunk_pages(pages)
    print(f"✓ Created {len(chunks)} chunks")
    
    # Step 3: Build vector store
    print("\n3️⃣  Building vector store...")
    store = create_vector_store(chunks)
    print(f"✓ Indexed {store.index.ntotal} vectors")
    
    # Step 4: Save vector store
    print("\n4️⃣  Saving vector store...")
    store.save(config.VECTOR_STORE_DIR, "rinvoq_pi")
    print(f"✓ Saved to {config.VECTOR_STORE_DIR}")
    
    # Step 5: Test retrieval
    print("\n5️⃣  Testing retrieval...")
    memory = ConversationMemory()
    retriever = create_retriever(store, memory)
    
    test_questions = [
        "What is the recommended dosage for ulcerative colitis?",
        "What are the boxed warnings?",
        "Is RINVOQ contraindicated in hepatic impairment?"
    ]
    
    for question in test_questions:
        print(f"\n❓ {question}")
        try:
            result = retriever.answer_question(question, "test-session")
            print(f"✓ {result['answer'][:150]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Quick start completed!")
    print("\nNext steps:")
    print("1. Start LM Studio on localhost:1234")
    print("2. Run backend: python main.py")
    print("3. Run frontend: cd ../frontend && npm run dev")
    print("4. Open http://localhost:3000")

if __name__ == "__main__":
    main()
