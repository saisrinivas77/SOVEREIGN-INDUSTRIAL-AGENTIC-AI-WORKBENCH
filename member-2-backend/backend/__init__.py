"""
SIH26117 Sovereign Industrial Agentic AI Workbench - Member 2 Backend Package
"""

import pkgutil
import sys
from pathlib import Path

__path__ = pkgutil.extend_path(__path__, __name__)

_backend_dir = Path(__file__).resolve().parent
_member_dir = _backend_dir.parent
_workspace_dir = _member_dir.parent

for p in (str(_member_dir), str(_workspace_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

