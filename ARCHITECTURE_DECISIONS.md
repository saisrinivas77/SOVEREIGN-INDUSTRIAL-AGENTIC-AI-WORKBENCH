# ARCHITECTURE DECISIONS

AD-001: FastAPI is the single application API boundary.
AD-002: LangGraph owns agent orchestration.
AD-003: ModelRouter hides model-specific implementations.
AD-004: ToolRegistry is the only agent action boundary.
AD-005: ChromaDB is local-only prototype vector store.
AD-006: Generated Python runs only in a network-disabled sandbox.
AD-007: Egress is default-deny/restricted; no cloud fallback.
AD-008: Canonical schemas are the integration contract.
AD-009: Deterministic routing is preferred for demo reliability.
AD-010: Security evidence must be observable, not merely claimed.
