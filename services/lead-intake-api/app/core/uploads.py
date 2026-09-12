from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from fastapi import HTTPException, UploadFile, status

ALLOWED_SUFFIXES = {".pdf", ".doc", ".docx"}
OLE_HEADER = bytes.fromhex("D0CF11E0A1B11AE1")


@dataclass(frozen=True)
class ValidatedDocument:
    content: bytes
    filename: str
    content_type: str
    sha256: str


def _bad_document(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


def _is_docx(content: bytes) -> bool:
    try:
        with ZipFile(BytesIO(content)) as archive:
            return "word/document.xml" in archive.namelist()
    except BadZipFile:
        return False


async def read_and_validate_resume(upload: UploadFile, max_bytes: int) -> ValidatedDocument:
    filename = upload.filename or ""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise _bad_document("Resume must be a PDF, DOC, or DOCX file")

    content = await upload.read(max_bytes + 1)
    if not content:
        raise _bad_document("Resume file is empty")
    if len(content) > max_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Resume exceeds 10 MB")

    valid_content = (
        (suffix == ".pdf" and content.startswith(b"%PDF-"))
        or (suffix == ".doc" and content.startswith(OLE_HEADER))
        or (suffix == ".docx" and _is_docx(content))
    )
    if not valid_content:
        raise _bad_document("Resume content does not match its declared file type")

    content_type = {
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }[suffix]
    return ValidatedDocument(
        content=content,
        filename=Path(filename).name,
        content_type=content_type,
        sha256=sha256(content).hexdigest(),
    )