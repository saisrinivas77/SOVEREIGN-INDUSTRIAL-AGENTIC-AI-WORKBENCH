# RAG CONTRACT v2

## Pipeline
INGEST
→ PARSE
→ OCR IF REQUIRED
→ CHUNK
→ EMBED LOCALLY
→ CHROMADB
→ RETRIEVE
→ OPTIONAL RERANK
→ SOURCE-PRESERVING CONTEXT

## Required metadata
document_id
filename
page
section
chunk_id
source_type
content_hash

## Retrieval output
Never return bare text without source metadata.

## Default
top_k = 5

## Citation
Final answers should cite:
filename + page + section when available.

## Grounding rule
The model must distinguish:
- source-supported fact
- inference
- missing evidence

Never fabricate source citations.

## Privacy
No remote embedding endpoint.
No remote vector database.
No remote document parser.

## Indexing
Documents are copied into the controlled workspace, parsed locally, embedded locally and stored locally.
