# TESTING CONTRACT v2

## Contract tests
Every boundary gets a test.

### ModelRouter
document → reasoning
coding → coding-capable
vision → vision
unavailable → local fallback/error
never → external

### Agent
plan → valid schema
step limit enforced
tool allowlist enforced
artifact verification performed

### Tools
invalid file ID rejected
path traversal rejected
unknown tool denied
sandbox timeout enforced

### RAG
index local document
retrieve relevant chunk
preserve page/source metadata
empty retrieval handled

### Security
external destination denied
local destination allowed
audit event created
no secret/content leakage in logs

### Sandbox
code runs
network unavailable
timeout works
filesystem restricted

### Artifacts
DOCX exists and opens
XLSX exists and opens
hash generated

## E2E smoke test
Scenario A:
inspection_report.pdf + inspection_photo.jpg + maintenance_sop.pdf
→ approval_note.docx

Scenario B:
equipment_data.csv
→ Python sandbox
→ results.xlsx
