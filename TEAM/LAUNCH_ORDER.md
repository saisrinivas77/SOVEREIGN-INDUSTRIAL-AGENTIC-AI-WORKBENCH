# AI AGENT LAUNCH ORDER

## Before coding
ALL 5:
1. Read AGENTS.md.
2. Read MASTER/.
3. Confirm assigned ownership.
4. Do not edit code outside ownership.

## Parallel phase
M1 frontend shell
M2 API + persistence
M3 agent + model router
M4 RAG/OCR/vision
M5 security/tools/sandbox/infra

## Integration checkpoints
Checkpoint 1: backend health + local model health
Checkpoint 2: upload + tool registry
Checkpoint 3: RAG + agent
Checkpoint 4: golden inspection E2E
Checkpoint 5: sandbox + XLSX
Checkpoint 6: sovereignty proof
