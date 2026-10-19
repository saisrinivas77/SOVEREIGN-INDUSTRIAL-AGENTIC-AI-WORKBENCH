"""
File upload endpoint conforming to MASTER/03_API_CONTRACTS.md.
"""

from fastapi import APIRouter, File, UploadFile
from backend.services.file_service import file_service
from backend.schemas.file import FileUploadResponse

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("", response_model=FileUploadResponse, status_code=200)
async def upload_file(file: UploadFile = File(...)) -> FileUploadResponse:
    """
    Multipart local upload with path traversal defense, MIME/extension checks, and workspace isolation.
    """
    content_disposition = file.headers.get("content-disposition", "")
    raw_filename = file.filename or "unnamed_file"

    # Extract exact client-supplied filename from Content-Disposition if present
    if 'filename="' in content_disposition:
        raw_header_filename = content_disposition.split('filename="', 1)[1].split('"', 1)[0]
    elif "filename=" in content_disposition:
        raw_header_filename = content_disposition.split("filename=", 1)[1].split(";", 1)[0].strip()
    else:
        raw_header_filename = raw_filename

    # If either raw_header_filename or raw_filename contains forbidden/security characters, pass that for security rejection
    if any(c in raw_header_filename for c in (":", "/", "\\", "..", "\x00", "%")):
        candidate_name = raw_header_filename
    elif any(c in raw_filename for c in (":", "/", "\\", "..", "\x00", "%")):
        candidate_name = raw_filename
    else:
        candidate_name = raw_filename

    return file_service.upload_file(
        filename=candidate_name,
        content_type=file.content_type or "application/octet-stream",
        file_obj=file.file,
    )
