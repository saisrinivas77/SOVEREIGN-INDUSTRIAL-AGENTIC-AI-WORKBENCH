# M5 AI CODING PROMPT — SECURITY + INTEGRATION

Role: Senior Platform/Security/Integration Engineer.

Read AGENTS.md and MASTER contracts first.

Allowed:
- member-5-security-integration/backend/security/**
- member-5-security-integration/backend/tools/**
- member-5-security-integration/sandbox/**
- member-5-security-integration/infra/**
- member-5-security-integration/docker/**

Goal:
Own the security boundary and integrate the five modules.

Required:
- ToolRegistry
- file/path validation
- sandboxed Python
- network restrictions/default-deny egress where environment permits
- network/audit monitor
- security status API support
- Docker Compose/local runtime
- integration branch
- final E2E testing

Security has priority over convenience.
Do not weaken network restrictions to make a feature work.
If a component needs external access, stop and report it.
