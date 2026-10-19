# CODING RULES v2

## Before coding
1. Read AGENTS.md.
2. Read relevant MASTER contracts.
3. Inspect existing code.
4. Find existing schemas/utilities.
5. State intended files before major implementation.

## Do
- type interfaces
- validate inputs
- use shared schemas
- write small functions
- keep dependencies minimal
- handle timeouts
- return structured errors
- add tests for boundary behavior
- use configuration, not hardcoded paths

## Don't
- duplicate schemas
- parse LLM prose with fragile string matching
- add hidden network calls
- use arbitrary shell execution
- use global mutable state
- bypass security
- modify another owner's module
- silently alter contracts

## AI-specific rule
If an LLM output is machine-consumed:
- request JSON
- validate it
- repair/retry in bounded fashion
- reject invalid output safely

## File handling
Use file IDs, not user-provided absolute paths.
