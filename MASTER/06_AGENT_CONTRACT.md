# AGENT CONTRACT v2

## Agent purpose
Execute bounded, auditable multi-step work using local models and registered tools.

## Required state
task_id
instruction
task_type
plan
current_step
tool_results
sources
artifacts
status
error

## Lifecycle
INTAKE
→ CLASSIFY
→ PLAN
→ ROUTE_MODEL
→ EXECUTE_STEP
→ OBSERVE
→ VERIFY
→ NEXT_STEP or COMPLETE

## Bounded execution
Default:
MAX_STEPS = 12
MAX_TOOL_RETRIES = 2
MAX_MODEL_RETRIES = 2
TASK_TIMEOUT = 10 minutes
TOOL_TIMEOUT = 60 seconds
SANDBOX_TIMEOUT = 30 seconds

Values are configurable centrally but must remain bounded.

## Tool policy
Agent may invoke only tools present in ToolRegistry and allowed for the task.

## Evidence policy
For knowledge-grounded decisions, the agent must retain source objects.
If evidence is insufficient, state that clearly.

## Verification policy
Every artifact must be existence/readability/hash verified.
Every code execution must return stdout/stderr/exit status.

## Security policy
Agent cannot:
- access raw network
- call external APIs
- execute host shell
- read secrets
- bypass path validation
- bypass sandbox
- invent tool names

## Prompt rule
Prompts must request structured output where machine parsing is required.
No downstream component may depend on exact wording.

## Human safety
This prototype is decision support. It must not claim that an AI-generated recommendation is an authorized industrial approval.
