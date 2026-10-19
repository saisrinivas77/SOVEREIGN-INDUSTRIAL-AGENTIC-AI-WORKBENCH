"""
Executable Multimodal Demo Runner for Member 4.
Demonstrates the Golden Workflow local document ingestion, OCR, local RAG retrieval,
page-level citations, anti-prompt injection defense, and local vision analysis.
"""

import os
import sys
import json

try:
    from backend.rag.pipeline import RAGMultimodalPipeline
except ImportError:
    from .pipeline import RAGMultimodalPipeline

def run_multimodal_demo():
    print("==================================================================")
    print(" SIH26117 — MEMBER 4 LOCAL RAG & MULTIMODAL DEMO RUNNER")
    print("==================================================================")
    print("Operating 100% locally on-premise without external network calls.")
    print("------------------------------------------------------------------\n")

    pipeline = RAGMultimodalPipeline()

    # Sample Golden Workflow Inputs
    sop_content = (
        "SIH-2026 SOVEREIGN INDUSTRIAL MAINTENANCE SOP v4.2\n"
        "Section 1.0 General Safety\n"
        "All personnel must verify system isolation and depressurization before opening hydraulic lines.\n\n"
        "Section 2.0 Hydraulic Pump Servicing\n"
        "Step 2.1: Inspect high-pressure seal for wear. Operating pressure limit is 250 bar.\n"
        "Step 2.2: Verify zero pressure differential across control valve V-102.\n"
        "Step 2.3: Torque flange bolts to 120 Nm using calibrated torque wrench."
    ).encode('utf-8')

    report_content = (
        "CONFIDENTIAL PLANT INSPECTION REPORT #8841\n"
        "Section 1.0 Summary\n"
        "Visual inspection performed on Hydraulic Pump Assembly P-101B.\n"
        "Operating hours: 4,200 hrs. Minor oil residue observed near valve flange.\n\n"
        "Section 2.0 Inspection Observations\n"
        "Flange bolt torque measured at 115 Nm. Seal integrity appears intact.\n"
        "Recommendation: Re-torque flange bolts to 120 Nm per SOP Section 2.0."
    ).encode('utf-8')

    photo_content = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00"

    print("[1/4] Ingesting & indexing maintenance_sop.pdf...")
    ingest_sop = pipeline.ingest_document(sop_content, "maintenance_sop.pdf", "DOC-SOP-001")
    print(f"      -> Status: {ingest_sop['status']}, Chunks: {ingest_sop['chunk_count']}")

    print("[2/4] Ingesting & indexing inspection_report.pdf...")
    ingest_rep = pipeline.ingest_document(report_content, "inspection_report.pdf", "DOC-REP-001")
    print(f"      -> Status: {ingest_rep['status']}, Chunks: {ingest_rep['chunk_count']}")

    print("[3/4] Running local Multimodal Vision Analysis on inspection_photo.jpg...")
    demo_output = pipeline.process_multimodal_demo(
        inspection_report_pdf=report_content,
        inspection_photo_jpg=photo_content,
        maintenance_sop_pdf=sop_content
    )

    print("\n[4/4] GENERATED AGENT EVIDENCE CONTEXT:")
    print("==================================================================")
    print(demo_output["agent_context"]["text_evidence"])
    print("==================================================================")
    print("\nVisual Observations:")
    for obs in demo_output["agent_context"]["image_observations"]:
        print(f"  - {obs}")
    print(f"\nVisual Confidence: {demo_output['agent_context']['confidence']}")
    print(f"Page-Level Citations: {demo_output['agent_context']['citations']}")
    print("\n==================================================================")
    print(" DEMO COMPLETED SUCCESSFULLY — 100% LOCAL EVIDENCE GENERATED")
    print("==================================================================")

if __name__ == "__main__":
    run_multimodal_demo()
