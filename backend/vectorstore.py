"""
Vector Store Module - Creates and manages FAISS vector store
Handles embedding generation and similarity search
"""
import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
from chunking import Chunk
import config


class VectorStore:
    """
    FAISS-based vector store for semantic search
    Uses sentence-transformers for embeddings
    """
    
    def __init__(self, model_name: str = config.EMBEDDING_MODEL):
        """
        Initialize vector store
        
        Args:
            model_name: Name of the sentence-transformer model
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []
        self.dimension = None
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Create embeddings for a list of texts
        
        Args:
            texts: List of text strings
        
        Returns:
            Numpy array of embeddings
        """
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def build_index(self, chunks: List[Chunk]):
        """
        Build FAISS index from chunks
        
        Args:
            chunks: List of Chunk objects
        """
        print(f"Building index from {len(chunks)} chunks...")
        
        # Store chunks
        self.chunks = chunks
        
        # Extract texts
        texts = [chunk.text for chunk in chunks]
        
        # Create embeddings
        embeddings = self.create_embeddings(texts)
        
        # Get dimension
        self.dimension = embeddings.shape[1]
        
        # Create FAISS index (L2 distance)
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Add embeddings to index
        self.index.add(embeddings.astype('float32'))
        
        print(f"Index built with {self.index.ntotal} vectors")
    
    def search(self, query: str, top_k: int = config.TOP_K_CHUNKS) -> List[Dict]:
        """
        Search for similar chunks
        
        Args:
            query: Query string
            top_k: Number of results to return
        
        Returns:
            List of dictionaries with chunk data and similarity scores
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index first.")
        
        # Create query embedding
        query_embedding = self.model.encode([query])
        
        # Search
        distances, indices = self.index.search(
            query_embedding.astype('float32'), top_k
        )
        
        # Prepare results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            chunk = self.chunks[idx]
            
            # Convert L2 distance to similarity score (inverse)
            similarity = 1 / (1 + distance)
            
            results.append({
                'text': chunk.text,
                'metadata': chunk.metadata,
                'chunk_id': chunk.chunk_id,
                'similarity': float(similarity),
                'rank': i + 1
            })
        
        return results
    
    def boost_results(self, results: List[Dict], query: str) -> List[Dict]:
        """
        Apply boosting based on query type and chunk metadata
        
        Args:
            results: Search results
            query: Original query
        
        Returns:
            Re-ranked results
        """
        query_lower = query.lower()
        
        # Boost logic
        for result in results:
            boost = 1.0
            metadata = result['metadata']
            section = metadata.get('section', '').lower()
            
            # Boost dosage tables for dosage questions
            if any(word in query_lower for word in ['dosage', 'dose', 'mg', 'administration']):
                if 'dosage' in section or 'administration' in section:
                    boost *= 1.5
                if metadata.get('has_table'):
                    boost *= 1.3
            
            # Boost warnings for safety questions
            if any(word in query_lower for word in ['warning', 'contraindication', 'adverse', 'risk', 'safety']):
                if 'warning' in section or 'contraindication' in section or 'adverse' in section:
                    boost *= 1.5
            
            # Boost boxed warnings
            if 'boxed' in query_lower or 'black box' in query_lower:
                if 'boxed' in section or 'warning' in section:
                    boost *= 2.0
            
            # Apply boost to similarity
            result['similarity'] *= boost
        
        # Re-sort by boosted similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results
    
    def search_with_boost(self, query: str, top_k: int = config.TOP_K_CHUNKS) -> List[Dict]:
        """
        Search with automatic boosting
        
        Args:
            query: Query string
            top_k: Number of results to return
        
        Returns:
            Boosted and re-ranked results
        """
        results = self.search(query, top_k * 2)  # Get more results for re-ranking
        results = self.boost_results(results, query)
        return results[:top_k]
    
    def save(self, directory: str, document_name: str):
        """
        Save vector store to disk
        
        Args:
            directory: Directory to save to
            document_name: Name of the document (used for filename)
        """
        os.makedirs(directory, exist_ok=True)
        
        # Sanitize document name
        safe_name = document_name.replace('.pdf', '').replace(' ', '_')
        
        # Save FAISS index
        index_path = os.path.join(directory, f"{safe_name}.index")
        faiss.write_index(self.index, index_path)
        
        # Save chunks and metadata
        metadata_path = os.path.join(directory, f"{safe_name}.pkl")
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'model_name': self.model_name,
                'dimension': self.dimension
            }, f)
        
        print(f"Vector store saved to {directory}")
    
    @classmethod
    def load(cls, directory: str, document_name: str):
        """
        Load vector store from disk
        
        Args:
            directory: Directory to load from
            document_name: Name of the document
            
        Returns:
            VectorStore instance
        """
        # Create new instance
        store = cls(model_name=config.EMBEDDING_MODEL)
        
        # Sanitize document name
        safe_name = document_name.replace('.pdf', '').replace(' ', '_')
        
        # Load FAISS index
        index_path = os.path.join(directory, f"{safe_name}.faiss")
        if not os.path.exists(index_path):
            index_path = os.path.join(directory, f"{safe_name}.index")
        
        store.index = faiss.read_index(index_path)
        
        # Load chunks and metadata
        metadata_path = os.path.join(directory, f"{safe_name}.pkl")
        with open(metadata_path, 'rb') as f:
            data = pickle.load(f)
            store.chunks = data['chunks']
            store.model_name = data['model_name']
            store.dimension = data['dimension']
        
        print(f"Vector store loaded from {directory}")
        return store


def create_vector_store(chunks: List[Chunk]) -> VectorStore:
    """
    Create and build vector store from chunks
    
    Args:
        chunks: List of Chunk objects
    
    Returns:
        VectorStore object
    """
    store = VectorStore()
    store.build_index(chunks)
    return store


if __name__ == "__main__":
    # Test vector store
    from ingest_pdf import ingest_pdf
    from chunking import chunk_pages
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        
        print("Ingesting PDF...")
        pages = ingest_pdf(pdf_path)
        
        print("Chunking...")
        chunks = chunk_pages(pages)
        
        print("Building vector store...")
        store = create_vector_store(chunks)
        
        print("\nTesting search...")
        results = store.search_with_boost("What is the recommended dosage?", top_k=3)
        
        for result in results:
            print(f"\nRank {result['rank']} (similarity: {result['similarity']:.3f})")
            print(f"Page {result['metadata']['page']}: {result['metadata']['section']}")
            print(f"Text: {result['text'][:200]}...")
