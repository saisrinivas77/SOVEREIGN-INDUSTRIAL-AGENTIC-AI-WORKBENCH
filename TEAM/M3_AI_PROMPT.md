# M3 AI CODING PROMPT — AGENT + MODEL ROUTER

Role: Senior AI/Agent Engineer.

Read AGENTS.md and MASTER contracts first.

Allowed:
- member-3-ai/backend/agents/**
- member-3-ai/backend/models/**
- member-3-ai/prompts/agent/**
- member-3-ai/prompts/models/**

Goal:
Implement bounded LangGraph orchestration and model abstraction.

Required:
- task classification
- deterministic model routing
- model adapters
- planner
- executor
- verifier
- bounded retries/steps
- canonical AgentPlan/AgentStep/ModelSelection outputs

Agent must call ModelRouter, never Ollama directly.
Agent must call registered tools, never arbitrary Python/shell.
Machine-consumed outputs must be structured and validated.
