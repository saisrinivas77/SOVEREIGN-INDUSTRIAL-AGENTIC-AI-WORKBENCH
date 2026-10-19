# SIH26117 — PROJECT CHARTER v2
## Sovereign Industrial Agentic AI Workbench

### 1. Mission
Build a demonstrable, self-hosted AI workbench for confidential industrial knowledge work. The prototype must prove that useful agentic AI can operate entirely inside an organization's controlled infrastructure without sending confidential content to cloud AI services.

### 2. Judge-facing promise
A user can upload a confidential industrial document, ask for a multi-step task, and receive an auditable answer or real artifact while every inference, retrieval, tool execution, and file operation remains local.

### 3. Mandatory proof points
P0:
- local inference
- at least two local model capabilities
- automatic model routing
- agent planning and bounded execution
- local file tools
- local RAG
- OCR
- vision
- sandboxed Python
- DOCX and XLSX artifacts
- audit trail
- network restriction/monitoring
- visible sovereignty evidence

### 4. Golden workflow
Inspection PDF + inspection image + maintenance SOP
→ local ingestion/OCR
→ agent plan
→ deterministic task classification
→ local model selection
→ RAG retrieval with page citations
→ vision analysis
→ evidence-grounded reasoning
→ approval_note.docx
→ artifact verification
→ audit record
→ sovereignty evidence

### 5. Secondary workflow
Equipment CSV
→ task classified as coding/data analysis
→ local coding-capable model
→ Python generated
→ isolated sandbox
→ execution result
→ verification
→ results.xlsx

### 6. Explicit non-goals
Do not build:
- cloud fallback
- model training/fine-tuning
- uncontrolled multi-agent swarm
- unrestricted shell access
- production IAM
- Kubernetes
- mobile app
- external telemetry
- external vector DB
- remote OCR/vision
- unnecessary memory systems

### 7. Reliability principle
For a 24-hour hackathon, deterministic infrastructure + bounded agent behavior is preferred over complicated autonomous behavior.

### 8. Data classification
Treat all uploaded documents as CONFIDENTIAL by default.
Never transmit confidential content outside the approved local boundary.
