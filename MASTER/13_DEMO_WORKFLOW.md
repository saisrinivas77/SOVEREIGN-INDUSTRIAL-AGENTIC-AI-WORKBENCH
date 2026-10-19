# FINAL JUDGING DEMO v2

## Demo setup
Use synthetic/public industrial sample data.
Pre-index knowledge documents before judging.
Have model health checked before presentation.
Do not depend on internet connectivity.

## Scene 1 — Sovereignty
Open Security Center first.
Show:
- network mode
- egress policy
- local model status
- no external AI endpoints configured

## Scene 2 — Upload
Upload inspection_report.pdf.
Show local file ID and local storage.

## Scene 3 — Agent
Prompt:
"Analyze this inspection report, check the applicable maintenance procedure,
review the inspection image, and prepare an approval note."

Show live plan.

## Scene 4 — Model routing
Show:
document reasoning → reasoning model
image → vision model

## Scene 5 — OCR/Vision
Show scanned page processing and image analysis.

## Scene 6 — RAG
Show retrieved SOP evidence with page citation.

## Scene 7 — Agent reasoning
Show evidence combination and recommendation.
Clearly label recommendation as AI decision support.

## Scene 8 — Artifact
Generate approval_note.docx.
Open/preview it.
Show verification/hash.

## Scene 9 — Coding
Ask:
"Analyze equipment_data.csv and identify abnormal readings."
Show coding-capable model → sandbox → execution → results.xlsx.

## Scene 10 — Security proof
Show audit timeline and network monitor.
Demonstrate blocked/absent external egress.
Emphasize that the workflow continued using local services.

## Judge questions to anticipate
Q: What happens if a model changes?
A: Model adapters isolate model-specific behavior.

Q: How do you prevent prompt output incompatibility?
A: Canonical schemas + validation + module contracts.

Q: How do you prevent data leakage?
A: No external AI dependencies + default-deny egress + local processing + sandbox + audit evidence.

Q: Can the system use a new open-weight model?
A: Register a new adapter/model capability without changing the agent contract.

Q: Is it truly agentic?
A: Show plan → tool → observation → verification → next step.

Q: What if evidence is missing?
A: The system reports insufficient local evidence instead of fabricating a citation.
