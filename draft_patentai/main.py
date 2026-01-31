from __future__ import annotations

import os
import tempfile
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.services.drafting import generate_draft
from src.services.extraction import extract_from_pdf, extract_from_text
from src.services.postprocess import postprocess_section
from src.services.structuring import extract_primitives
from src.utils.text import normalize_newlines

app = FastAPI(title="DraftPatenAI")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "web")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"error": "index.html not found"}, status_code=404)


@app.post("/generate")
async def generate(
    text: Optional[str] = Form(default=None),
    pdf: Optional[UploadFile] = File(default=None),
    mode: str = Form(...),
):
    if mode not in {"patent", "research"}:
        raise HTTPException(status_code=400, detail="mode must be patent or research")

    if not text and not pdf:
        raise HTTPException(status_code=400, detail="Provide text or pdf")

    document_id = "doc_local"
    if pdf:
        suffix = os.path.splitext(pdf.filename or "upload.pdf")[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await pdf.read()
            tmp.write(content)
            tmp_path = tmp.name
        try:
            extraction = extract_from_pdf(document_id, tmp_path)
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
    else:
        normalized = normalize_newlines(text or "")
        extraction = extract_from_text(document_id, normalized)

    primitives = extract_primitives(extraction, domain=mode)
    draft_sections = generate_draft(primitives, mode=mode)
    final_text = postprocess_section(draft_sections, document_id, section=mode)

    return {"output": final_text}

