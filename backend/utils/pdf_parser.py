"""PDF and document parsing utilities"""
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DocumentParser:
    """Parse various document formats to extract text"""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_content: PDF file bytes
            
        Returns:
            Extracted text
        """
        try:
            # Try PyPDF2 first
            try:
                import PyPDF2
                pdf_file = io.BytesIO(file_content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                logger.info(f"Extracted {len(text)} characters from PDF")
                return text.strip()
            except ImportError:
                logger.warning("PyPDF2 not installed, falling back to basic extraction")
                # Fallback: try to decode as text
                return file_content.decode('utf-8', errors='ignore')
                
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """
        Extract text from DOCX file
        
        Args:
            file_content: DOCX file bytes
            
        Returns:
            Extracted text
        """
        try:
            try:
                import docx
                doc_file = io.BytesIO(file_content)
                doc = docx.Document(doc_file)
                
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                logger.info(f"Extracted {len(text)} characters from DOCX")
                return text.strip()
            except ImportError:
                logger.warning("python-docx not installed")
                raise ValueError("DOCX parsing requires python-docx library")
                
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file_content: bytes) -> str:
        """
        Extract text from TXT file
        
        Args:
            file_content: TXT file bytes
            
        Returns:
            Extracted text
        """
        try:
            text = file_content.decode('utf-8', errors='ignore')
            logger.info(f"Extracted {len(text)} characters from TXT")
            return text.strip()
        except Exception as e:
            logger.error(f"TXT extraction failed: {e}")
            raise ValueError(f"Failed to extract text from TXT: {str(e)}")
    
    @staticmethod
    def extract_text(file_content: bytes, filename: str) -> str:
        """
        Extract text from file based on extension
        
        Args:
            file_content: File bytes
            filename: Original filename with extension
            
        Returns:
            Extracted text
        """
        extension = filename.lower().split('.')[-1]
        
        if extension == 'pdf':
            return DocumentParser.extract_text_from_pdf(file_content)
        elif extension in ['docx', 'doc']:
            return DocumentParser.extract_text_from_docx(file_content)
        elif extension == 'txt':
            return DocumentParser.extract_text_from_txt(file_content)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

def get_document_parser() -> DocumentParser:
    """Get DocumentParser instance"""
    return DocumentParser()
