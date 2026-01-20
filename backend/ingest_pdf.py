"""
PDF Ingestion Module - Extracts text from FDA prescribing information PDFs
Preserves page numbers, section headings, and structure
"""
import re
import fitz  # PyMuPDF
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class PageContent:
    """Represents extracted content from a single page"""
    page_number: int
    text: str
    sections: List[str]
    has_table: bool
    document_name: str


class PDFIngestor:
    """
    Extracts text from FDA prescribing information PDFs
    Preserves structure, sections, and metadata
    """
    
    # Regex pattern for FDA section headings (e.g., "1.4", "2.6", "5.1")
    SECTION_PATTERN = re.compile(r'^\s*(\d+\.?\d*)\s+([A-Z][A-Za-z\s,&\(\)]+)', re.MULTILINE)
    
    def __init__(self, pdf_path: str):
        """
        Initialize PDF ingestor
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.document_name = pdf_path.split('/')[-1].split('\\')[-1]
        self.doc = None
    
    def open(self):
        """Open the PDF document"""
        self.doc = fitz.open(self.pdf_path)
        return self
    
    def close(self):
        """Close the PDF document"""
        if self.doc:
            self.doc.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self.open()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def extract_sections(self, text: str) -> List[str]:
        """
        Extract section headings from text
        
        Args:
            text: Page text
        
        Returns:
            List of section headings found on the page
        """
        sections = []
        matches = self.SECTION_PATTERN.finditer(text)
        
        for match in matches:
            section_num = match.group(1)
            section_title = match.group(2).strip()
            sections.append(f"{section_num} {section_title}")
        
        return sections
    
    def detect_table(self, page) -> bool:
        """
        Detect if page contains tables
        
        Args:
            page: PyMuPDF page object
        
        Returns:
            True if table detected, False otherwise
        """
        # Check for table-like structures (multiple tabs, structured spacing)
        text = page.get_text()
        
        # Simple heuristic: multiple tab characters or aligned columns
        tab_count = text.count('\t')
        if tab_count > 10:
            return True
        
        # Check for PyMuPDF table detection
        try:
            tables = page.find_tables()
            # TableFinder object needs to be converted to list
            return tables is not None and len(tables.tables) > 0
        except:
            return False
    
    def extract_page(self, page_num: int) -> PageContent:
        """
        Extract content from a single page
        
        Args:
            page_num: Page number (0-indexed)
        
        Returns:
            PageContent object with extracted data
        """
        page = self.doc[page_num]
        
        # Extract text
        text = page.get_text("text")
        
        # Clean up text (remove excessive whitespace, but preserve structure)
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Max 2 consecutive newlines
        
        # Extract sections
        sections = self.extract_sections(text)
        
        # Detect tables
        has_table = self.detect_table(page)
        
        return PageContent(
            page_number=page_num + 1,  # 1-indexed for user display
            text=text,
            sections=sections,
            has_table=has_table,
            document_name=self.document_name
        )
    
    def extract_all_pages(self) -> List[PageContent]:
        """
        Extract content from all pages
        
        Returns:
            List of PageContent objects
        """
        pages = []
        
        for page_num in range(len(self.doc)):
            page_content = self.extract_page(page_num)
            pages.append(page_content)
        
        return pages
    
    def get_page_count(self) -> int:
        """Get total number of pages"""
        return len(self.doc) if self.doc else 0
    
    @staticmethod
    def merge_sections_across_pages(pages: List[PageContent]) -> List[PageContent]:
        """
        Carry forward section context across pages
        If a page doesn't have a section heading, inherit from previous page
        
        Args:
            pages: List of PageContent objects
        
        Returns:
            Updated list with inherited sections
        """
        current_section = []
        
        for page in pages:
            if page.sections:
                current_section = page.sections
            elif current_section:
                # Inherit from previous page
                page.sections = current_section.copy()
        
        return pages


def ingest_pdf(pdf_path: str) -> List[PageContent]:
    """
    Main function to ingest a PDF file
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        List of PageContent objects with extracted data
    """
    with PDFIngestor(pdf_path) as ingestor:
        pages = ingestor.extract_all_pages()
        pages = PDFIngestor.merge_sections_across_pages(pages)
    
    return pages


if __name__ == "__main__":
    # Test ingestion
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        pages = ingest_pdf(pdf_path)
        
        print(f"Extracted {len(pages)} pages")
        print(f"\nFirst page preview:")
        print(f"Page: {pages[0].page_number}")
        print(f"Sections: {pages[0].sections}")
        print(f"Has table: {pages[0].has_table}")
        print(f"Text preview: {pages[0].text[:500]}...")
