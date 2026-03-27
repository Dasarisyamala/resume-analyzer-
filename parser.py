import PyPDF2

def extract_text(file_path):
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        # Return a special error string to be handled by the caller
        return f"[PDF_ERROR] {str(e)}"
    return text