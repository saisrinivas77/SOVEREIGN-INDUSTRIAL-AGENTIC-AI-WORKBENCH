"""
Path & Workspace Security Validator.
Enforces strict boundary confinement, prevents traversal (../, ..\\),
rejects arbitrary host paths, symlink escapes, and resolves files via canonical File IDs.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, Optional
import shutil

try:
    from infra.runtime_config import RuntimeConfig
except ImportError:
    import sys
    from pathlib import Path
    _pkg_root = Path(__file__).resolve().parent.parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))
    from infra.runtime_config import RuntimeConfig

class SecurityPathViolationError(PermissionError):
    """Raised when a path access violates security boundaries or attempts traversal."""
    pass

class PathValidator:
    """Manages secure file resolution and workspace path confinement."""

    def __init__(self, workspace_dir: Optional[Path] = None, outputs_dir: Optional[Path] = None):
        self.workspace_dir = (workspace_dir or RuntimeConfig.WORKSPACE_DIR).resolve()
        self.uploads_dir = (self.workspace_dir / "uploads").resolve()
        self.outputs_dir = (outputs_dir or RuntimeConfig.OUTPUTS_DIR).resolve()
        self.sandboxes_dir = (self.workspace_dir / "sandboxes").resolve()

        # In-memory mapping of file_id -> secure local Path
        self._file_registry: Dict[str, Path] = {}
        self._filename_registry: Dict[str, str] = {}

        # Ensure directories exist
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.sandboxes_dir.mkdir(parents=True, exist_ok=True)

    def register_file(self, file_id: str, filename: str, content: bytes) -> Path:
        """
        Securely store an uploaded or created file under a canonical file_id in the uploads workspace.
        """
        if not re.match(r"^[a-zA-Z0-9_\-\.]+$", file_id):
            raise SecurityPathViolationError(f"Invalid file_id format: {file_id}")

        safe_filename = self.sanitize_filename(filename)
        # Store in unique subfolder per file_id to prevent name collisions
        file_dir = (self.uploads_dir / file_id).resolve()
        file_dir.mkdir(parents=True, exist_ok=True)
        target_path = (file_dir / safe_filename).resolve()

        # Validate that target_path is strictly within uploads_dir
        self.validate_path_within_root(target_path, self.uploads_dir)

        with open(target_path, "wb") as f:
            f.write(content)

        self._file_registry[file_id] = target_path
        self._filename_registry[file_id] = safe_filename
        return target_path

    def register_existing_path(self, file_id: str, path: Path, filename: Optional[str] = None) -> Path:
        """Register an existing validated path under a file_id."""
        resolved = path.resolve()
        self.validate_path_confinement(resolved)
        self._file_registry[file_id] = resolved
        self._filename_registry[file_id] = filename or path.name
        return resolved

    def resolve_file_id(self, file_id: str) -> Path:
        """
        Resolve a canonical file_id to its validated filesystem path.
        Rejects traversal attempts or unrecognized file IDs.
        """
        if not file_id or not isinstance(file_id, str):
            raise SecurityPathViolationError("file_id must be a non-empty string.")

        # Check for explicit traversal patterns inside the file_id string
        if ".." in file_id or "/" in file_id or "\\" in file_id or "\x00" in file_id:
            raise SecurityPathViolationError(f"Traversals or path separators forbidden in file_id: {file_id}")

        if file_id in self._file_registry:
            path = self._file_registry[file_id]
            if path.exists():
                self.validate_path_confinement(path)
                return path

        # Check in uploads directory directly
        candidate_dir = (self.uploads_dir / file_id).resolve()
        if candidate_dir.exists() and candidate_dir.is_dir():
            files = list(candidate_dir.glob("*"))
            if files and files[0].is_file():
                self.validate_path_confinement(files[0])
                self._file_registry[file_id] = files[0]
                return files[0]

        raise FileNotFoundError(f"File ID '{file_id}' not found in controlled workspace registry.")

    def get_filename(self, file_id: str) -> str:
        """Get original filename for a registered file_id."""
        return self._filename_registry.get(file_id, f"{file_id}.dat")

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent directory traversal or reserved character attacks."""
        if not filename:
            return "unnamed_file.dat"
        # Strip path elements
        name = Path(filename).name
        # Remove null bytes, control chars, path separators
        clean_name = re.sub(r'[\x00-\x1f\\/\?%*:|"<>]', '_', name)
        # Prevent hidden / special traversal names
        if clean_name in {".", "..", "...", ""}:
            clean_name = "sanitized_file.dat"
        return clean_name

    def validate_path_confinement(self, target_path: Path) -> Path:
        """
        Validate that the target path is strictly confined within one of the approved roots:
        - WORKSPACE_DIR (uploads, sandboxes)
        - OUTPUTS_DIR
        """
        resolved = Path(target_path).resolve()

        # Check if contained in workspace_dir or outputs_dir
        in_workspace = self._is_subpath(resolved, self.workspace_dir)
        in_outputs = self._is_subpath(resolved, self.outputs_dir)

        if not (in_workspace or in_outputs):
            raise SecurityPathViolationError(
                f"Path '{target_path}' is outside approved sovereign roots ({self.workspace_dir}, {self.outputs_dir})."
            )
        return resolved

    def validate_path_within_root(self, target_path: Path, root_dir: Path) -> Path:
        """Validate that target_path is strictly within root_dir."""
        resolved_root = Path(root_dir).resolve()
        resolved_target = Path(target_path).resolve()

        if not self._is_subpath(resolved_target, resolved_root):
            raise SecurityPathViolationError(
                f"Path '{target_path}' escapes root directory '{root_dir}'."
            )
        return resolved_target

    def validate_raw_path_string(self, path_str: str) -> None:
        """
        Reject path strings containing traversal sequences or absolute host roots.
        """
        if not path_str or not isinstance(path_str, str):
            return

        # Check for traversal
        if ".." in path_str or "/../" in path_str or "\\..\\" in path_str:
            raise SecurityPathViolationError(f"Directory traversal detected in path: '{path_str}'")

        # Check for null bytes
        if "\x00" in path_str:
            raise SecurityPathViolationError(f"Null byte detected in path: '{path_str}'")

        # Check for absolute POSIX host root escapes
        posix_host_roots = ["/etc", "/var", "/root", "/sys", "/proc", "/bin", "/sbin", "/usr", "/tmp", "/dev", "/opt"]
        for hr in posix_host_roots:
            if path_str.startswith(hr):
                raise SecurityPathViolationError(f"Access to host system directory '{path_str}' is forbidden.")

        # Check for absolute Windows paths (e.g. C:\...)
        if re.match(r"^[a-zA-Z]:[\\/]", path_str):
            # Check if it starts with approved workspace or outputs directory
            try:
                candidate_path = Path(path_str).resolve()
                self.validate_path_confinement(candidate_path)
            except Exception:
                raise SecurityPathViolationError(f"Access to host Windows system path '{path_str}' is forbidden.")

    @staticmethod
    def _is_subpath(path: Path, root: Path) -> bool:
        """Check if path is a subpath of root (canonical)."""
        try:
            path.relative_to(root)
            return True
        except ValueError:
            return False

# Global Singleton instance
path_validator = PathValidator()
