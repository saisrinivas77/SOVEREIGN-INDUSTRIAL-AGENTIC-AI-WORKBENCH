# M4 AI CODING PROMPT — RAG + OCR + VISION

Role: Senior Retrieval and Multimodal Engineer.

Read AGENTS.md and MASTER contracts first.

Allowed:
- member-4-rag-multimodal/backend/rag/**
- member-4-rag-multimodal/backend/ocr/**
- member-4-rag-multimodal/backend/vision/**
- member-4-rag-multimodal/prompts/rag/**

Goal:
Build local document ingestion, OCR, retrieval and image understanding.

Required:
- PyMuPDF parsing
- Tesseract OCR for scanned content
- local embeddings
- ChromaDB
- source/page metadata
- local vision model integration
- citation-preserving retrieval

No remote embeddings.
No remote OCR.
No cloud vision.
Do not modify agent/API modules.
