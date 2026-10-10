from pypdf import PdfReader
import docx
import os

def load_document(file_path):
    text = ""
    lower_path = file_path.lower()

    if lower_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        for page_no,page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n[PAGE {page_no+1}]\n{page_text}"

    elif lower_path.endswith(".docx"):
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    elif lower_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    return text