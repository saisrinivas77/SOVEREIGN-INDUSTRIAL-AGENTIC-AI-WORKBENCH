"""
Sandbox Execution Environment & Ephemeral Workspace Manager.
Prepares isolated execution directories, stages input files, and collects outputs safely.
"""

import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Optional

try:
    from backend.security.path_validator import path_validator
    from infra.runtime_config import RuntimeConfig
except ImportError:
    import sys
    from pathlib import Path
    _pkg_root = Path(__file__).resolve().parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))
    from backend.security.path_validator import path_validator
    from infra.runtime_config import RuntimeConfig

class SandboxEnvironment:
    """
    Manages an ephemeral sandbox working directory for an execution run.
    """

    def __init__(self, run_id: Optional[str] = None):
        self.run_id = run_id or f"run_{uuid.uuid4().hex[:8]}"
        self.sandbox_dir = (RuntimeConfig.SANDBOX_DIR / self.run_id).resolve()
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        self.staged_files: List[str] = []

    def stage_input_files(self, file_ids: List[str]) -> List[Path]:
        """
        Securely copy registered input files into the isolated sandbox environment.
        """
        staged_paths = []
        for fid in file_ids:
            if not fid:
                continue
            src_path = path_validator.resolve_file_id(fid)
            dest_name = path_validator.get_filename(fid)
            dest_path = (self.sandbox_dir / dest_name).resolve()

            # Ensure dest_path is strictly inside sandbox_dir
            path_validator.validate_path_within_root(dest_path, self.sandbox_dir)

            shutil.copy2(src_path, dest_path)
            self.staged_files.append(dest_name)
            staged_paths.append(dest_path)
        return staged_paths

    def write_script(self, code: str, filename: str = "main.py") -> Path:
        """Write the Python script to be executed in the sandbox."""
        script_path = (self.sandbox_dir / filename).resolve()
        path_validator.validate_path_within_root(script_path, self.sandbox_dir)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)
        return script_path

    def collect_output_files(self, exclude_files: Optional[List[str]] = None) -> Dict[str, bytes]:
        """
        Collect all generated non-script output files from the sandbox workspace.
        """
        exclude = set(exclude_files or [])
        exclude.add("main.py")
        exclude.add("__pycache__")
        exclude.update(self.staged_files)

        output_files: Dict[str, bytes] = {}
        for item in self.sandbox_dir.rglob("*"):
            if item.is_file() and item.name not in exclude and not item.name.endswith(".pyc"):
                rel_name = str(item.relative_to(self.sandbox_dir))
                with open(item, "rb") as f:
                    output_files[rel_name] = f.read()

        return output_files

    def cleanup(self) -> None:
        """Safely remove the ephemeral sandbox directory."""
        if self.sandbox_dir.exists():
            shutil.rmtree(self.sandbox_dir, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
