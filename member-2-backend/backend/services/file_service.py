"""
File management service conforming to MASTER/03_API_CONTRACTS.md and MASTER/04_DATA_SCHEMAS.md.
Enforces size, extension, MIME, and path traversal protections.
"""

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO
from ..config import UPLOADS_DIR, settings
from .database import db
from .audit_service import audit_service
from .security_service import security_service
from ..schemas.file import FileUploadResponse, FileRecord


class FileService:
    def __init__(self, database=db, audit=audit_service, security=security_service):
        self.db = database
        self.audit = audit
        self.security = security
        self.upload_dir = UPLOADS_DIR

    def upload_file(self, filename: str, content_type: str, file_obj: BinaryIO) -> FileUploadResponse:
        self.security.record_local_call("file_service")

        # 1. Sanitize & validate filename against traversal
        safe_filename = self.security.validate_safe_filename(filename)

        # 2. Validate file extension
        ext = Path(safe_filename).suffix.lower()
        if ext not in settings.allowed_extensions:
            self.security.record_blocked_attempt("Disallowed file extension", {"extension": ext, "filename": safe_filename})
            raise ValueError(f"Disallowed file extension '{ext}'. Allowed extensions: {', '.join(sorted(settings.allowed_extensions))}")

        # 3. Validate MIME type (basic check or fallback)
        clean_mime = (content_type or "").split(";")[0].strip().lower()
        if clean_mime and clean_mime not in settings.allowed_mime_types:
            self.security.record_blocked_attempt("Disallowed MIME type", {"mime_type": clean_mime, "filename": safe_filename})
            raise ValueError(f"Disallowed MIME type '{clean_mime}'.")

        if not clean_mime:
            clean_mime = "application/octet-stream"

        # 4. Read file content with size limit enforcement
        data = file_obj.read()
        file_size = len(data)
        if file_size > settings.max_file_size_bytes:
            self.security.record_blocked_attempt("File exceeds maximum allowed size", {"size": file_size, "limit": settings.max_file_size_bytes})
            raise ValueError(f"File size ({file_size} bytes) exceeds maximum limit of {settings.max_file_size_bytes} bytes.")

        if file_size == 0:
            raise ValueError("Uploaded file is empty (0 bytes).")

        # 5. Generate internal canonical File ID
        file_id = f"FILE-{uuid.uuid4().hex[:8].upper()}"

        # 6. Compute SHA-256 hash
        sha256_hash = hashlib.sha256(data).hexdigest()

        # 7. Secure storage inside controlled workspace
        destination_filename = f"{file_id}_{safe_filename}"
        destination_path = self.upload_dir / destination_filename

        with open(destination_path, "wb") as f:
            f.write(data)

        # 8. Persist file metadata
        uploaded_at = datetime.now(timezone.utc).isoformat()
        self.db.save_file(
            file_id=file_id,
            filename=safe_filename,
            mime_type=clean_mime,
            size=file_size,
            sha256=sha256_hash,
            stored_path=str(destination_path),
            uploaded_at=uploaded_at,
        )

        # 9. Audit event
        self.audit.log_event(
            event_type="file_access",
            actor="user",
            component="file_service",
            status="success",
            metadata={
                "file_id": file_id,
                "filename": safe_filename,
                "mime_type": clean_mime,
                "size": file_size,
                "sha256": sha256_hash,
            },
        )

        # 10. Return response without host path
        return FileUploadResponse(
            file_id=file_id,
            filename=safe_filename,
            mime_type=clean_mime,
            size=file_size,
        )

    def get_file(self, file_id: str) -> FileRecord | None:
        row = self.db.get_file(file_id)
        if not row:
            return None
        return FileRecord(
            file_id=row["file_id"],
            filename=row["filename"],
            mime_type=row["mime_type"],
            size=row["size"],
            sha256=row["sha256"],
            stored_path=row["stored_path"],
            uploaded_at=row["uploaded_at"],
        )

    def validate_file_ids_exist(self, file_ids: list[str]) -> None:
        if not file_ids:
            return
        files = self.db.get_files_by_ids(file_ids)
        found_ids = {f["file_id"] for f in files}
        missing = set(file_ids) - found_ids
        if missing:
            raise ValueError(f"Referenced file_id(s) do not exist: {', '.join(sorted(missing))}")


file_service = FileService()
