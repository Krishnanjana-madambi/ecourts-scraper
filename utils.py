# utils.py
import os
from typing import List

# --- Folder creation helper ---
def ensure_dir(path: str):
    """
    Create a folder if it doesn't exist.
    """
    os.makedirs(path, exist_ok=True)

# --- Safe path join helper ---
def safe_join(*parts) -> str:
    """
    Join multiple path parts and normalize.
    """
    return os.path.normpath(os.path.join(*parts))

# --- PDF merge helper ---
try:
    from PyPDF2 import PdfMerger
except ImportError:
    PdfMerger = None  # safe fallback if PyPDF2 not installed

def merge_pdfs(pdf_list: List[str], output_path: str):
    """
    Merge multiple PDFs into a single PDF.
    Requires PyPDF2 to be installed.
    """
    if PdfMerger is None:
        raise RuntimeError("PyPDF2 is not installed. Run `pip install PyPDF2` to use merge_pdfs.")

    merger = PdfMerger()
    for pdf_file in pdf_list:
        merger.append(pdf_file)

    # Ensure output folder exists
    ensure_dir(os.path.dirname(output_path))

    merger.write(output_path)
    merger.close()
    return output_path
