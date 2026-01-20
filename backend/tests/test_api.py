"""
API Integration Tests
Test the FastAPI endpoints
"""
import requests
import os
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("\n🔍 Testing health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✓ Status: {response.status_code}")
        
        data = response.json()
        print(f"✓ LM Studio connected: {data.get('lm_studio_connected')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_upload_pdf():
    """Test PDF upload endpoint"""
    print("\n📤 Testing PDF upload...")
    
    pdf_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'rinvoq_pi.pdf'
    )
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return None
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': ('rinvoq_pi.pdf', f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        print(f"✓ Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Document ID: {data.get('document_id')}")
            print(f"✓ Pages: {data.get('page_count')}")
            print(f"✓ Chunks: {data.get('chunk_count')}")
            return data.get('document_id')
        else:
            print(f"❌ Error: {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_chat(document_id):
    """Test chat endpoint"""
    print("\n💬 Testing chat...")
    
    if not document_id:
        print("❌ No document ID provided")
        return False
    
    test_questions = [
        "What is the recommended dosage for ulcerative colitis?",
        "What are the boxed warnings?",
        "Is RINVOQ contraindicated in hepatic impairment?"
    ]
    
    session_id = "test-session-" + str(int(time.time()))
    
    for question in test_questions:
        print(f"\n❓ {question}")
        
        try:
            payload = {
                "question": question,
                "session_id": session_id,
                "document_id": document_id
            }
            
            response = requests.post(f"{BASE_URL}/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                print(f"✓ Answer: {answer[:150]}...")
                
                # Check for citations
                if "(Page" in answer:
                    print("✓ Citations present")
                else:
                    print("⚠ No citations found")
            else:
                print(f"❌ Error: {response.text}")
                return False
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    return True


def test_history(session_id):
    """Test history endpoint"""
    print("\n📜 Testing history...")
    
    try:
        response = requests.get(f"{BASE_URL}/history/{session_id}")
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get('messages', [])
            print(f"✓ Retrieved {len(messages)} messages")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_list_documents():
    """Test list documents endpoint"""
    print("\n📚 Testing list documents...")
    
    try:
        response = requests.get(f"{BASE_URL}/documents")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Documents: {data.get('count')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all API tests"""
    print("=" * 60)
    print("Drug Information Chatbot - API Integration Tests")
    print("=" * 60)
    
    print("\n⚠ Make sure the backend is running on localhost:8000")
    print("⚠ Make sure LM Studio is running on localhost:1234")
    
    input("\nPress Enter to continue...")
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Health check failed. Is the backend running?")
        return
    
    # Test 2: List documents
    test_list_documents()
    
    # Test 3: Upload PDF
    document_id = test_upload_pdf()
    
    if not document_id:
        print("\n❌ PDF upload failed. Cannot proceed with chat tests.")
        return
    
    # Wait for processing to complete
    print("\n⏳ Waiting for processing to complete...")
    time.sleep(5)
    
    # Test 4: Chat
    if not test_chat(document_id):
        print("\n❌ Chat tests failed.")
        return
    
    # Test 5: History
    test_history(f"test-session-{int(time.time())}")
    
    print("\n" + "=" * 60)
    print("✅ All API tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
