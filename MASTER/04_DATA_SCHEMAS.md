# DATA SCHEMAS v2
## Canonical wire formats

## Task
{
  "task_id": "TASK-001",
  "instruction": "string",
  "file_ids": [],
  "task_type": "document|coding|vision|general",
  "status": "queued|running|completed|failed",
  "created_at": "ISO-8601"
}

## AgentPlan
{
  "task_id": "TASK-001",
  "goal": "string",
  "steps": [
    {
      "step_id": 1,
      "action": "string",
      "tool": "string|null",
      "expected_output": "string"
    }
  ]
}

## AgentStep
{
  "step_id": 1,
  "action": "string",
  "tool": "string|null",
  "status": "pending|running|completed|failed",
  "started_at": "ISO-8601",
  "finished_at": "ISO-8601|null",
  "result": {},
  "error": null
}

## ModelSelection
{
  "task_type": "document|coding|vision|general",
  "capability": "reasoning|coding|vision",
  "model_id": "string",
  "reason": "string",
  "confidence": 0.0
}

## ToolCall
{
  "call_id": "CALL-001",
  "tool": "string",
  "arguments": {},
  "status": "completed|failed|denied",
  "result": {},
  "duration_ms": 0
}

## Source
{
  "document_id": "DOC-001",
  "filename": "maintenance_sop.pdf",
  "page": 17,
  "section": "4.2",
  "chunk_id": "string",
  "score": 0.0,
  "text": "string"
}

## Artifact
{
  "artifact_id": "ART-001",
  "filename": "approval_note.docx",
  "type": "docx",
  "path": "outputs/ART-001/approval_note.docx",
  "sha256": "string",
  "verified": true
}

## AuditEvent
{
  "event_id": "AUD-001",
  "timestamp": "ISO-8601",
  "event_type": "task|model_call|tool_call|file_access|network|security|artifact",
  "actor": "user|agent|system",
  "component": "string",
  "status": "success|failure|denied",
  "metadata": {}
}

## Compatibility
New fields must be additive unless an approved contract version changes.
Do not rename or reinterpret existing fields during the hackathon.
