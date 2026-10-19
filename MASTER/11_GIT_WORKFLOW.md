# GIT WORKFLOW v2

## Branches
main
integration
feature/m1-frontend
feature/m2-backend
feature/m3-ai
feature/m4-rag
feature/m5-security

## Integration owner
M5.

## Merge sequence
feature branch
→ self-test
→ pull/merge into integration
→ contract tests
→ E2E smoke test
→ main

## Freeze points
At hour 1:
architecture/contracts freeze.

At hour 12:
P0 feature freeze.

At hour 18:
demo freeze.

After demo freeze:
only critical bug fixes.

## Commit format
feat:
fix:
test:
refactor:
docs:
chore:

## Merge checklist
- ownership respected
- contracts unchanged or approved
- tests pass
- no external dependency
- security checks pass
- no secrets
