import os
import pdfplumber
import PyPDF2
from typing import Dict, Any, List

class FileLoader:
    """Utility to load content from different file formats."""

    @staticmethod
    def load_file(file_path: str) -> str:
        """Reads content based on file extension."""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext == '.pdf':
            return FileLoader._read_pdf(file_path)
        elif ext in ['.txt', '.md']:
            return FileLoader._read_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def _read_pdf(file_path: str) -> str:
        """Extracts text from PDF using pdfplumber as primary and PyPDF2 as fallback."""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            if not text.strip():
                raise Exception("pdfplumber returned empty text")
        except Exception:
            # Fallback to PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        
        return text

    @staticmethod
    def _read_text(file_path: str) -> str:
        """Reads content from text or markdown files."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
