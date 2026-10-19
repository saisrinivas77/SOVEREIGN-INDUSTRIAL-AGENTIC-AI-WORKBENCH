"""
Artifacts API endpoints for Sovereign AI Workbench.
"""

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.services.database import db
from backend.config import ARTIFACTS_DIR

router = APIRouter(prefix="/artifacts", tags=["Artifacts"])


@router.get("", status_code=200)
async def list_artifacts():
    artifacts = db.list_all_artifacts()
    return {"artifacts": artifacts}


@router.get("/{artifact_id}/download")
async def download_artifact(artifact_id: str):
    artifacts = db.list_all_artifacts()
    target = next(
        (a for a in artifacts if a.get("artifact_id") == artifact_id or a.get("id") == artifact_id),
        None
    )
    
    if not target:
        raise HTTPException(status_code=404, detail=f"Artifact '{artifact_id}' not found.")
    
    raw_path = target.get("path", "")
    filename = target.get("filename", "download")
    file_path = Path(raw_path)
    
    if not file_path.is_absolute() or not file_path.exists():
        # Candidate 1: relative to current working directory
        candidate_1 = Path.cwd() / raw_path
        # Candidate 2: relative to ARTIFACTS_DIR parent
        candidate_2 = ARTIFACTS_DIR.parent / raw_path
        candidate_3 = ARTIFACTS_DIR.parent.parent / raw_path
        
        if candidate_1.exists():
            file_path = candidate_1
        elif candidate_2.exists():
            file_path = candidate_2
        elif candidate_3.exists():
            file_path = candidate_3
        else:
            # Candidate 4: Recursive search in ARTIFACTS_DIR for filename
            found = list(ARTIFACTS_DIR.rglob(filename))
            if found:
                file_path = found[0]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Artifact file '{filename}' does not exist on disk.")
        
    return FileResponse(path=file_path, filename=filename)
