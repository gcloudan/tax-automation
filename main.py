"""
pdf-service/main.py
FastAPI microservice: accepts a PDF upload → returns extracted text + AUD amounts.
Called by n8n when an email has a PDF attachment.
"""

import re
from typing import Optional

import fitz  # PyMuPDF
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="PDF Extractor for Tax Automation", version="1.0.0")

# Regex to find AUD dollar amounts like $1,234.56 or $450.00 or $12.5
AUD_PATTERN = re.compile(r"\$\s?([\d,]+(?:\.\d{1,2})?)")


class ExtractResponse(BaseModel):
    text: str
    page_count: int
    amounts_aud: list[float]
    vendor_hint: Optional[str] = None
    char_count: int


def find_aud_amounts(text: str) -> list[float]:
    """Extract all dollar amounts from text, deduplicated and sorted."""
    raw = AUD_PATTERN.findall(text)
    amounts = set()
    for r in raw:
        try:
            amounts.add(float(r.replace(",", "")))
        except ValueError:
            pass
    return sorted(amounts, reverse=True)


def guess_vendor(text: str) -> Optional[str]:
    """
    Simple heuristic: look for common vendor name patterns near the top of the doc.
    Replace/extend this list with your real vendors.
    """
    vendors = [
        "Biggins Home Services", "Biggins",
        "AliExpress", "Amazon", "Bunnings", "Apple",
        "JB Hi-Fi", "Jaycar", "DigitalOcean", "AWS",
        "Invoice2go",
    ]
    text_upper = text.upper()
    for v in vendors:
        if v.upper() in text_upper:
            return v
    return None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
async def extract_pdf(file: UploadFile = File(...)):
    """
    Accept a PDF file, extract all text using PyMuPDF, find AUD amounts.
    n8n calls this with the raw PDF binary from a Gmail attachment.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = await file.read()

    try:
        doc = fitz.open(stream=contents, filetype="pdf")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse PDF: {str(e)}")

    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    amounts = find_aud_amounts(full_text)
    vendor = guess_vendor(full_text)

    return ExtractResponse(
        text=full_text[:8000],  # Truncate to avoid overwhelming AI context
        page_count=doc.page_count if hasattr(doc, "page_count") else 0,
        amounts_aud=amounts,
        vendor_hint=vendor,
        char_count=len(full_text),
    )


@app.post("/extract-text-only")
async def extract_text_only(file: UploadFile = File(...)):
    """Lightweight endpoint — just returns raw text string. For quick AI ingestion."""
    contents = await file.read()
    try:
        doc = fitz.open(stream=contents, filetype="pdf")
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    text = "".join(page.get_text() for page in doc)
    doc.close()
    return JSONResponse({"text": text[:8000]})
