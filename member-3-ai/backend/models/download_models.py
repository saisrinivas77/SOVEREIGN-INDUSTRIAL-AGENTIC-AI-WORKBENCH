"""Local Model Downloader and Provisioning Script for SIH26117 Workbench.

Conforms strictly to MASTER/05_MODEL_CONTRACT.md and MASTER/09_SECURITY_SOVEREIGNTY.md.
Pulls approved local Qwen models into the local Ollama runtime and verifies local availability.

Approved Model Set:
- Reasoning / Main: Qwen3 / Qwen2.5 (3B / 7B / 8B / 14B)
- Coding: Qwen3-Coder / Qwen2.5-Coder (3B / 7B / 8B / 14B)
- Vision / Multimodal: Qwen2.5-VL / LLaVA (3B / 7B)
- Embeddings: nomic-embed-text / bge-m3 (Local RAG)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from typing import Dict, List, Literal, Optional
import httpx

HardwareProfile = Literal["small", "medium", "large"]

MODEL_PROFILES: Dict[HardwareProfile, Dict[str, str]] = {
    "small": {
        "reasoning": "qwen2.5:3b-instruct",
        "coding": "qwen2.5-coder:3b",
        "vision": "qwen2.5-vl:3b",
        "embedding": "nomic-embed-text"
    },
    "medium": {
        "reasoning": "qwen2.5:7b-instruct",
        "coding": "qwen2.5-coder:7b",
        "vision": "qwen2.5-vl:7b",
        "embedding": "nomic-embed-text"
    },
    "large": {
        "reasoning": "qwen2.5:14b-instruct",
        "coding": "qwen2.5-coder:14b",
        "vision": "qwen2.5-vl:7b",
        "embedding": "bge-m3"
    }
}


def check_ollama_service(base_url: str = "http://127.0.0.1:11434") -> bool:
    """Check if local Ollama daemon is reachable."""
    try:
        with httpx.Client(timeout=2.0) as client:
            resp = client.get(f"{base_url}/api/version")
            return resp.status_code == 200
    except Exception:
        return False


def pull_model_via_api(model_name: str, base_url: str = "http://127.0.0.1:11434") -> bool:
    """Pull model via Ollama HTTP API with progress reporting."""
    print(f"\n[MODEL DOWNLOADER] Initiating local pull for '{model_name}'...")
    endpoint = f"{base_url}/api/pull"
    payload = {"name": model_name, "stream": False}

    try:
        with httpx.Client(timeout=1800.0) as client:  # 30 min timeout for download
            resp = client.post(endpoint, json=payload)
            if resp.status_code == 200:
                print(f"[MODEL DOWNLOADER] Successfully pulled '{model_name}' to local runtime.")
                return True
            else:
                print(f"[MODEL DOWNLOADER] Failed to pull '{model_name}': HTTP {resp.status_code} -> {resp.text}")
                return False
    except Exception as e:
        print(f"[MODEL DOWNLOADER] Error pulling '{model_name}': {e}")
        return False


def pull_model_via_cli(model_name: str) -> bool:
    """Pull model using the 'ollama pull' command line."""
    ollama_path = shutil.which("ollama")
    if not ollama_path:
        print("[MODEL DOWNLOADER] 'ollama' executable not found in PATH.")
        return False

    print(f"\n[MODEL DOWNLOADER] Running 'ollama pull {model_name}'...")
    try:
        proc = subprocess.run(["ollama", "pull", model_name], check=True)
        return proc.returncode == 0
    except Exception as e:
        print(f"[MODEL DOWNLOADER] CLI pull failed: {e}")
        return False


def download_all_models(
    profile: HardwareProfile = "medium",
    base_url: str = "http://127.0.0.1:11434"
) -> Dict[str, bool]:
    """Download all required models for the specified hardware profile."""
    models_to_pull = MODEL_PROFILES.get(profile, MODEL_PROFILES["medium"])
    results: Dict[str, bool] = {}

    print("=" * 60)
    print("SOVEREIGN AI WORKBENCH — LOCAL MODEL PROVISIONING")
    print(f"Hardware Profile: {profile.upper()}")
    print(f"Target Models: {json.dumps(models_to_pull, indent=2)}")
    print("=" * 60)

    is_running = check_ollama_service(base_url)
    has_cli = bool(shutil.which("ollama"))

    if not is_running and not has_cli:
        print("\n[INFO] Local Ollama service is not running on http://127.0.0.1:11434.")
        print("To download & host models locally on your system:")
        print("1. Install Ollama from: https://ollama.com/download/windows")
        print("2. Run the following commands in PowerShell/Terminal:")
        for cap, m_id in models_to_pull.items():
            print(f"     ollama pull {m_id}")
        print("\n3. Or run 'ollama serve' and re-execute this script:")
        print("     python member-3-ai/backend/models/download_models.py")
        print("\n[STATUS] Sovereign AI Workbench is fully operational in OFFLINE mode")
        print("using the built-in deterministic LocalAdapter engine.\n")
        return {k: False for k in models_to_pull.values()}

    for capability, model_id in models_to_pull.items():
        print(f"\n---> Provisioning {capability.upper()} Model: {model_id}")
        success = False
        if is_running:
            success = pull_model_via_api(model_id, base_url)
        if not success and has_cli:
            success = pull_model_via_cli(model_id)
        results[model_id] = success

    print("\n" + "=" * 60)
    print("PROVISIONING SUMMARY:")
    for m, status in results.items():
        status_str = "READY (LOCAL)" if status else "PENDING / OFFLINE"
        print(f"  - {m:<25}: {status_str}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download sovereign local models for SIH26117 Workbench.")
    parser.add_argument(
        "--profile",
        choices=["small", "medium", "large"],
        default="medium",
        help="Hardware profile based on available GPU VRAM (default: medium)"
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:11434",
        help="Local Ollama endpoint URL (default: http://127.0.0.1:11434)"
    )
    args = parser.parse_args()
    download_all_models(profile=args.profile, base_url=args.url)
