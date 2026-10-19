# MASTER ARCHITECTURE v2
## Single source of architectural truth

## 1. System topology

                         USER
                           |
                           v
                 +--------------------+
                 | Next.js Workbench   |
                 +----------+---------+
                            |
                      HTTPS/local HTTP
                            |
                            v
                 +--------------------+
                 | FastAPI API Layer  |
                 +----------+---------+
                            |
             +--------------+--------------+
             |                             |
             v                             v
      +-------------+               +-------------+
      | Task/Session|               | Audit       |
      | Service     |               | Service     |
      +------+------+               +-------------+
             |
             v
      +------------------+
      | Agent Orchestrator|
      | LangGraph         |
      +---------+---------+
                |
                v
      +------------------+
      | Task Classifier   |
      | deterministic     |
      +---------+---------+
                |
                v
      +------------------+
      | Model Router      |
      +---------+---------+
                |
        +-------+-------+
        |       |       |
        v       v       v
    Reasoning Coding  Vision
      Adapter Adapter Adapter
        |       |       |
        +-------+-------+
                |
                v
           Ollama/local
                |
                v
      +----------------------+
      | Registered Tool Layer|
      +----------+-----------+
                 |
       +---------+---------+----------+
       |         |         |          |
       v         v         v          v
      RAG      Files     Sandbox   Artifacts
       |                             |
       v                             v
   ChromaDB                    DOCX/XLSX/Code

SECURITY PLANE:
network egress control + DNS restriction + sandbox + path validation +
tool allowlist + audit logging + local-only storage + security monitor

## 2. Non-negotiable boundaries
B1. Frontend never calls Ollama directly.
B2. Agent never calls Ollama directly; it calls ModelRouter.
B3. Agent never imports implementation-specific tool modules; it calls ToolRegistry.
B4. Generated code never executes on the host.
B5. RAG never sends documents to a remote service.
B6. Uploaded files are accessible only through validated workspace paths.
B7. Security events are recorded by the audit/security layer.
B8. No feature may silently introduce an external network dependency.

## 3. Process responsibilities
Frontend = presentation.
FastAPI = API boundary.
Agent = orchestration.
Task Classifier = deterministic intent classification.
Model Router = capability/model selection.
Adapters = model-specific translation.
Tools = controlled actions.
RAG = retrieval only.
Sandbox = code execution only.
Artifact engine = output creation only.
Security = enforcement and evidence.

## 4. State ownership
UI state belongs to frontend.
Task state belongs to backend/agent service.
Knowledge state belongs to RAG.
Audit state belongs to audit service.
Model availability belongs to model service.
No shared mutable state across modules without a contract.

## 5. Failure philosophy
Every boundary must fail closed for security and fail explicitly for functionality.
Never silently fall back to a cloud service.
