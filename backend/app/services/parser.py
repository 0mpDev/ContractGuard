import io
import os
import shutil

import fitz
import pytesseract
from PIL import Image

# Tesseract location: honour TESSERACT_CMD if set, otherwise use whatever is on
# PATH (Linux/macOS/Docker). Only fall back to the default Windows install path
# if it actually exists, so the same code runs on a laptop and in production.
_WIN_DEFAULT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
_tesseract_cmd = os.getenv("TESSERACT_CMD") or shutil.which("tesseract")
if not _tesseract_cmd and os.path.exists(_WIN_DEFAULT):
    _tesseract_cmd = _WIN_DEFAULT
if _tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd


class InvalidPDFError(ValueError):
    """Raised when the uploaded bytes can't be opened as a PDF."""


def extract_text_from_pdf(pdf_bytes):
    pages = extract_pages_from_pdf(pdf_bytes)
    return "\n".join(page["text"] for page in pages)


def extract_pages_from_pdf(pdf_bytes):
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        raise InvalidPDFError("The uploaded file is not a readable PDF.") from e

    pages = []

    try:
        for index, page in enumerate(doc):
            text = page.get_text()
            is_scanned = False

            # if page is empty/scanned -> use OCR
            if len(text.strip()) < 30:
                is_scanned = True
                text = _ocr_page(page)

            pages.append({
                "page": index + 1,
                "text": text,
                "is_scanned": is_scanned,
            })
    finally:
        doc.close()

    return pages


def _ocr_page(page) -> str:
    try:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        return pytesseract.image_to_string(img, lang="eng")
    except Exception as e:
        print(f"OCR failed on page: {e}")
        return ""
