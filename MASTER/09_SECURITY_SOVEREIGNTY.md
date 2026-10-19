# SECURITY + SOVEREIGNTY CONTRACT v2

## Security objective
Prevent and demonstrate prevention of confidential data leaving the local trust boundary.

## Defense in depth
L1 Application allowlists
L2 Container/network restrictions
L3 OS/firewall egress controls where available
L4 Sandbox isolation
L5 Audit logs
L6 Local-only storage
L7 Runtime network monitoring

## Trust boundary
TRUSTED:
- user's workstation/server
- local backend
- local model runtime
- local vector DB
- local database
- controlled workspace

UNTRUSTED:
- public internet
- external AI APIs
- external storage
- third-party telemetry

## Egress policy
Default deny.

Only explicitly approved local destinations are permitted.

## External AI prohibition
Never call:
- OpenAI
- Anthropic
- Google Gemini
- remote Hugging Face inference
- arbitrary external LLM endpoints
- external OCR/vision services

## Secrets
No API keys are required for core operation.
If a future optional integration needs a secret, it is prohibited in the 24-hour prototype unless explicitly approved.

## Network evidence
Record:
- destination
- port
- protocol
- allowed/blocked
- component
- timestamp

Do not record confidential payloads.

## Security dashboard
Show:
- external calls
- external AI calls
- blocked attempts
- local model calls
- local RAG calls
- local tool calls
- current network mode

## Critical demo
Disconnect/block internet or run with egress denied.
Execute the golden workflow.
Show successful local operation.
Show network monitor proving external attempts are blocked/absent.

## Important wording
Do not claim mathematically absolute "zero leakage" solely from an application counter.
Claim:
"External egress is denied/restricted and no external AI/data calls were observed during the demonstrated workflow," backed by technical evidence.
