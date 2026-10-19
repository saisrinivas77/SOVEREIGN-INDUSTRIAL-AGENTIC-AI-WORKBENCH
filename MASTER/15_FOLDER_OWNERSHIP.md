# FOLDER OWNERSHIP v2

## M1 — Frontend
member-1-platform/frontend/**
Allowed shared read:
MASTER/**, API schemas

## M2 — Backend
member-2-backend/backend/api/**
member-2-backend/backend/services/**
member-2-backend/backend/schemas/**

## M3 — AI
member-3-ai/backend/agents/**
member-3-ai/backend/models/**
member-3-ai/prompts/agent/**
member-3-ai/prompts/models/**

## M4 — RAG / Multimodal
member-4-rag-multimodal/backend/rag/**
member-4-rag-multimodal/backend/ocr/**
member-4-rag-multimodal/backend/vision/**
member-4-rag-multimodal/prompts/rag/**

## M5 — Security / Integration
member-5-security-integration/backend/security/**
member-5-security-integration/backend/tools/**
member-5-security-integration/sandbox/**
member-5-security-integration/infra/**
member-5-security-integration/docker/**

## Protected
MASTER/**
shared schemas after freeze
root configuration
integration branch

## If a cross-module change is necessary
Create a change request in CHANGE_REQUESTS.md and get M5 approval.
