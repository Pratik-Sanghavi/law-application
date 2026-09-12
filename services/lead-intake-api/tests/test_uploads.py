from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.core.uploads import read_and_validate_resume


@pytest.mark.asyncio
async def test_accepts_pdf() -> None:
    upload = UploadFile(filename="resume.pdf", file=BytesIO(b"%PDF-1.7\nresume"))
    document = await read_and_validate_resume(upload, max_bytes=1024)
    assert document.content_type == "application/pdf"


@pytest.mark.asyncio
async def test_rejects_wrong_extension() -> None:
    upload = UploadFile(filename="resume.txt", file=BytesIO(b"hello"))
    with pytest.raises(HTTPException, match="PDF, DOC, or DOCX"):
        await read_and_validate_resume(upload, max_bytes=1024)


@pytest.mark.asyncio
async def test_rejects_mismatched_pdf_content() -> None:
    upload = UploadFile(filename="resume.pdf", file=BytesIO(b"not a PDF"))
    with pytest.raises(HTTPException, match="does not match"):
        await read_and_validate_resume(upload, max_bytes=1024)