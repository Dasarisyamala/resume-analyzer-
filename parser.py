import os

import docx2txt
import PyPDF2


def _extract_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text


def extract_text(file_path):
    ext = os.path.splitext(file_path.lower())[1]
    try:
        if ext == ".pdf":
            return _extract_pdf(file_path)
        if ext == ".docx":
            return docx2txt.process(file_path)
        raise ValueError("Unsupported file type")
    except Exception as exc:
        return f"[PARSE_ERROR] {exc}"