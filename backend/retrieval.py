"""
Retrieval Module - Orchestrates RAG pipeline
Combines vector search, memory, and LLM generation
"""
from typing import List, Dict, Optional
from vectorstore import VectorStore
from memory import ConversationMemory
from llm_client import LMStudioClient, get_llm_client
from prompts import SYSTEM_PROMPT, create_user_prompt
import config


class RAGRetriever:
    """
    Retrieval-Augmented Generation orchestrator
    Handles the complete RAG pipeline
    """
    
    def __init__(self, 
                 vector_store: VectorStore,
                 memory: ConversationMemory,
                 llm_client: Optional[LMStudioClient] = None):
        """
        Initialize RAG retriever
        
        Args:
            vector_store: VectorStore instance
            memory: ConversationMemory instance
            llm_client: Optional LMStudioClient (creates one if not provided)
        """
        self.vector_store = vector_store
        self.memory = memory
        self._llm_client = llm_client  # Store the provided client or None
    
    @property
    def llm_client(self) -> LMStudioClient:
        """Lazy load LLM client only when needed"""
        if self._llm_client is None:
            self._llm_client = get_llm_client()
        return self._llm_client
    
    def retrieve_context(self, query: str, top_k: int = config.TOP_K_CHUNKS) -> List[Dict]:
        """
        Retrieve relevant context chunks for a query with intelligent re-ranking
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
        
        Returns:
            List of retrieved chunks with metadata
        """
        results = self.vector_store.search_with_boost(query, top_k=top_k * 2)  # Get more candidates
        
        # Filter by similarity threshold
        filtered_results = [
            r for r in results 
            if r['similarity'] >= config.SIMILARITY_THRESHOLD
        ]
        
        # Re-rank based on query type and section relevance
        query_lower = query.lower()
        
        for result in filtered_results:
            section = result.get('metadata', {}).get('section', '').lower()
            
            # Boost dosing sections for dosage questions
            if any(word in query_lower for word in ['dosage', 'dose', 'how much', 'mg']):
                if 'dosage' in section or 'administration' in section or '2.' in section:
                    result['similarity'] += 0.1
            
            # Boost warnings/precautions for safety questions
            elif any(word in query_lower for word in ['warning', 'caution', 'risk', 'adverse']):
                if 'warning' in section or 'adverse' in section or 'precaution' in section:
                    result['similarity'] += 0.1
            
            # Boost contraindications section
            elif any(word in query_lower for word in ['contraindication', 'should not', 'cannot']):
                if 'contraindication' in section or '4.' in section:
                    result['similarity'] += 0.1
        
        # Re-sort by adjusted similarity
        filtered_results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Return top_k after re-ranking
        return filtered_results[:top_k]
    
    def extract_citations(self, chunks: List[Dict]) -> str:
        """
        Extract page citations from chunks
        
        Args:
            chunks: List of chunk dictionaries
        
        Returns:
            Formatted citation string
        """
        pages = sorted(set(chunk['metadata']['page'] for chunk in chunks))
        
        if len(pages) == 1:
            return f"(Page {pages[0]})"
        elif len(pages) == 2:
            return f"(Pages {pages[0]} and {pages[1]})"
        else:
            page_list = ", ".join(str(p) for p in pages[:-1])
            return f"(Pages {page_list}, and {pages[-1]})"
    
    def generate_answer(self, 
                       query: str, 
                       session_id: str,
                       retrieved_chunks: List[Dict]) -> Dict:
        """
        Generate answer using LLM
        
        Args:
            query: User query
            session_id: Session identifier
            retrieved_chunks: Retrieved context chunks
        
        Returns:
            Dictionary with answer and metadata
        """
        # Get conversation history
        history = self.memory.get_last_n_pairs(session_id, config.MAX_HISTORY_MESSAGES)
        
        # Create user prompt
        user_prompt = create_user_prompt(retrieved_chunks, history, query)
        
        # Generate answer
        answer = self.llm_client.generate_answer(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            conversation_history=[]  # History already in user_prompt
        )
        
        # Extract citations from answer (if LLM included them)
        # Or append citations if not present
        if "(Page" not in answer:
            citations = self.extract_citations(retrieved_chunks)
            answer = f"{answer} {citations}"
        
        # Store in memory
        self.memory.add_message(session_id, "user", query)
        self.memory.add_message(session_id, "assistant", answer)
        
        return {
            'answer': answer,
            'sources': retrieved_chunks,
            'session_id': session_id
        }
    
    def answer_question(self, query: str, session_id: str) -> Dict:
        """
        Complete RAG pipeline: retrieve and generate answer
        
        Args:
            query: User query
            session_id: Session identifier
        
        Returns:
            Dictionary with answer and metadata
        """
        # Retrieve context
        chunks = self.retrieve_context(query)
        
        if not chunks:
            # No relevant context found
            answer = "This information is not available in the provided prescribing document."
            self.memory.add_message(session_id, "user", query)
            self.memory.add_message(session_id, "assistant", answer)
            
            return {
                'answer': answer,
                'sources': [],
                'session_id': session_id
            }
        
        # Generate answer
        return self.generate_answer(query, session_id, chunks)
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of messages
        """
        return self.memory.get_history(session_id)
    
    def clear_conversation(self, session_id: str):
        """
        Clear conversation history
        
        Args:
            session_id: Session identifier
        """
        self.memory.clear_session(session_id)


def create_retriever(vector_store: VectorStore, memory: ConversationMemory) -> RAGRetriever:
    """
    Create RAG retriever
    
    Args:
        vector_store: VectorStore instance
        memory: ConversationMemory instance
    
    Returns:
        RAGRetriever instance
    """
    return RAGRetriever(vector_store, memory)


if __name__ == "__main__":
    # Test retrieval
    from ingest_pdf import ingest_pdf
    from chunking import chunk_pages
    from vectorstore import create_vector_store
    from memory import ConversationMemory
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        
        print("Setting up RAG pipeline...")
        
        # Ingest and chunk
        pages = ingest_pdf(pdf_path)
        chunks = chunk_pages(pages)
        
        # Create vector store
        store = create_vector_store(chunks)
        
        # Create memory
        mem = ConversationMemory()
        
        # Create retriever
        retriever = create_retriever(store, mem)
        
        # Test query
        session = "test-session"
        query = "What is the recommended dosage for ulcerative colitis?"
        
        print(f"\nQuery: {query}")
        result = retriever.answer_question(query, session)
        
        print(f"\nAnswer: {result['answer']}")
        print(f"\nSources used: {len(result['sources'])}")
