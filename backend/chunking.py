"""
Chunking Module - Splits extracted pages into semantically coherent chunks
Preserves metadata (page, section, document name)
"""
import re
from typing import List, Dict
from dataclasses import dataclass
from ingest_pdf import PageContent
import config


@dataclass
class Chunk:
    """Represents a text chunk with metadata"""
    text: str
    metadata: Dict
    chunk_id: str


class SmartChunker:
    """
    Splits page content into chunks while preserving context
    Ensures chunks are sized appropriately for embedding models
    """
    
    def __init__(self, chunk_size: int = config.CHUNK_SIZE, 
                 overlap: int = config.CHUNK_OVERLAP):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target chunk size in tokens (approximate)
            overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation: 1 token ≈ 4 chars)
        
        Args:
            text: Input text
        
        Returns:
            Estimated token count
        """
        return len(text) // 4
    
    def split_by_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Input text
        
        Returns:
            List of sentences
        """
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def split_by_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs
        
        Args:
            text: Input text
        
        Returns:
            List of paragraphs
        """
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def create_chunks_from_page(self, page: PageContent) -> List[Chunk]:
        """
        Create chunks from a single page
        
        Args:
            page: PageContent object
        
        Returns:
            List of Chunk objects
        """
        chunks = []
        
        # Split into paragraphs first
        paragraphs = self.split_by_paragraphs(page.text)
        
        current_chunk = ""
        current_tokens = 0
        
        for para in paragraphs:
            para_tokens = self.estimate_tokens(para)
            
            # If paragraph alone exceeds chunk size, split by sentences
            if para_tokens > self.chunk_size:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk, page, len(chunks)
                    ))
                    current_chunk = ""
                    current_tokens = 0
                
                # Split large paragraph
                sentences = self.split_by_sentences(para)
                for sentence in sentences:
                    sent_tokens = self.estimate_tokens(sentence)
                    
                    if current_tokens + sent_tokens > self.chunk_size:
                        if current_chunk:
                            chunks.append(self._create_chunk(
                                current_chunk, page, len(chunks)
                            ))
                            # Overlap: keep last portion
                            overlap_text = self._get_overlap(current_chunk)
                            current_chunk = overlap_text + " " + sentence
                            current_tokens = self.estimate_tokens(current_chunk)
                        else:
                            current_chunk = sentence
                            current_tokens = sent_tokens
                    else:
                        current_chunk += " " + sentence
                        current_tokens += sent_tokens
            else:
                # Check if adding this paragraph exceeds chunk size
                if current_tokens + para_tokens > self.chunk_size:
                    # Save current chunk
                    if current_chunk:
                        chunks.append(self._create_chunk(
                            current_chunk, page, len(chunks)
                        ))
                        # Overlap: keep last portion
                        overlap_text = self._get_overlap(current_chunk)
                        current_chunk = overlap_text + "\n\n" + para
                        current_tokens = self.estimate_tokens(current_chunk)
                    else:
                        current_chunk = para
                        current_tokens = para_tokens
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + para
                    else:
                        current_chunk = para
                    current_tokens += para_tokens
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                current_chunk, page, len(chunks)
            ))
        
        return chunks
    
    def _get_overlap(self, text: str) -> str:
        """
        Get overlap portion from end of text
        
        Args:
            text: Input text
        
        Returns:
            Overlap text
        """
        sentences = self.split_by_sentences(text)
        
        overlap_text = ""
        overlap_tokens = 0
        
        # Take last few sentences for overlap
        for sentence in reversed(sentences):
            sent_tokens = self.estimate_tokens(sentence)
            if overlap_tokens + sent_tokens <= self.overlap:
                overlap_text = sentence + " " + overlap_text
                overlap_tokens += sent_tokens
            else:
                break
        
        return overlap_text.strip()
    
    def _create_chunk(self, text: str, page: PageContent, chunk_index: int) -> Chunk:
        """
        Create a Chunk object with metadata
        
        Args:
            text: Chunk text
            page: Source PageContent
            chunk_index: Index of chunk within page
        
        Returns:
            Chunk object
        """
        # Determine primary section (first section if multiple)
        section = page.sections[0] if page.sections else "Unknown Section"
        
        metadata = {
            "page": page.page_number,
            "section": section,
            "document": page.document_name,
            "has_table": page.has_table,
            "chunk_index": chunk_index
        }
        
        chunk_id = f"{page.document_name}_p{page.page_number}_c{chunk_index}"
        
        return Chunk(
            text=text.strip(),
            metadata=metadata,
            chunk_id=chunk_id
        )
    
    def create_chunks_from_pages(self, pages: List[PageContent]) -> List[Chunk]:
        """
        Create chunks from multiple pages
        
        Args:
            pages: List of PageContent objects
        
        Returns:
            List of all chunks
        """
        all_chunks = []
        
        for page in pages:
            page_chunks = self.create_chunks_from_page(page)
            all_chunks.extend(page_chunks)
        
        return all_chunks


def chunk_pages(pages: List[PageContent]) -> List[Chunk]:
    """
    Main function to chunk pages
    
    Args:
        pages: List of PageContent objects
    
    Returns:
        List of Chunk objects
    """
    chunker = SmartChunker()
    return chunker.create_chunks_from_pages(pages)


if __name__ == "__main__":
    # Test chunking
    from ingest_pdf import ingest_pdf
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        pages = ingest_pdf(pdf_path)
        chunks = chunk_pages(pages)
        
        print(f"Created {len(chunks)} chunks from {len(pages)} pages")
        print(f"\nFirst chunk:")
        print(f"ID: {chunks[0].chunk_id}")
        print(f"Metadata: {chunks[0].metadata}")
        print(f"Text preview: {chunks[0].text[:300]}...")
