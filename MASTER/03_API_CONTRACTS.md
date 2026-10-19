# API CONTRACTS v2

Base path: /api/v1

## POST /tasks
Request:
{
  "instruction": "string",
  "file_ids": ["string"]
}
Response:
{
  "task_id": "TASK-...",
  "status": "queued"
}

## POST /tasks/{task_id}/run
Response:
{
  "task_id": "string",
  "status": "running"
}

## GET /tasks/{task_id}
Response:
{
  "task_id": "string",
  "status": "queued|running|completed|failed",
  "task_type": "document|coding|vision|general",
  "steps": [],
  "artifacts": [],
  "error": null
}

## POST /files
Multipart local upload.
Response:
{
  "file_id": "FILE-...",
  "filename": "string",
  "mime_type": "string",
  "size": 0
}

## POST /knowledge/index
Request:
{"file_id":"FILE-..."}
Response:
{"document_id":"DOC-...","status":"indexed"}

## POST /knowledge/search
Request:
{"query":"string","top_k":5}
Response:
{"results":[]}

## GET /models
Response:
{"models":[]}

## GET /health
Response:
{
  "status":"healthy|degraded",
  "services":{}
}

## GET /security/status
Response:
{
  "network_mode":"restricted",
  "external_calls":0,
  "external_ai_calls":0,
  "blocked_attempts":0,
  "local_calls":0
}

## GET /audit/tasks/{task_id}
Response:
{"events":[]}

## Error envelope
{
  "error": {
    "code": "MACHINE_READABLE_CODE",
    "message": "safe human-readable message",
    "request_id": "REQ-..."
  }
}

Never return raw stack traces or secrets.
