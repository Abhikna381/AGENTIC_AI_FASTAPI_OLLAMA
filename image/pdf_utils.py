from pypdf import PdfReader
import io

def extract_pdf_text(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def chunk_text(text, chunk_size=800):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]