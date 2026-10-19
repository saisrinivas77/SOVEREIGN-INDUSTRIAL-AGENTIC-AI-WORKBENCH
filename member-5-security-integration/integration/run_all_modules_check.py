"""
Full Verification Runner for Member 5 Modules.
Demonstrates live execution of all 7 canonical tools, the sandbox, the security manager,
the audit service, and both Golden and Coding E2E workflows.
"""

import sys
import json
from pathlib import Path

pkg_root = Path(__file__).resolve().parent.parent
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from backend.tools.registry import tool_registry
from backend.security.security_manager import security_manager
from backend.security.network_guard import network_guard
from backend.security.audit_service import audit_service
from integration.workflow_runner import workflow_runner
from integration.security_reporter import security_reporter

def main():
    print("=" * 70)
    print("MEMBER 5: FULL MODULE VERIFICATION REPORT")
    print("=" * 70)

    # 1. Registered Tools Verification
    print("\n[1/5] TOOL REGISTRY INSPECTION:")
    tools = tool_registry.list_tools()
    print(f"Total Registered Tools: {len(tools)}")
    for t in tools:
        print(f"  + Tool: {t['name']:<18} | Perm: {t['permission']:<16} | Timeout: {t['timeout_seconds']}s")

    # 2. Golden Workflow Run
    print("\n[2/5] RUNNING GOLDEN WORKFLOW (PDF + Image + SOP -> DOCX):")
    g_res = workflow_runner.run_golden_workflow()
    print(f"  Status: {'SUCCESS' if g_res.success else 'FAILED'}")
    print(f"  Task ID: {g_res.task_id}")
    print(f"  Steps Completed ({len(g_res.steps)}):")
    for s in g_res.steps:
        print(f"    - Step {s['step_id']}: {s['action']} [Tool: {s['tool']}] -> Success: {s['success']}")
    print(f"  Generated Artifacts ({len(g_res.artifacts)}):")
    for a in g_res.artifacts:
        print(f"    - {a['filename']} (Type: {a['type']}, SHA256: {a['sha256'][:16]}..., Verified: {a['verified']})")

    # 3. Coding Workflow Run
    print("\n[3/5] RUNNING CODING WORKFLOW (CSV -> Sandbox -> XLSX):")
    c_res = workflow_runner.run_coding_workflow()
    print(f"  Status: {'SUCCESS' if c_res.success else 'FAILED'}")
    print(f"  Task ID: {c_res.task_id}")
    print(f"  Steps Completed ({len(c_res.steps)}):")
    for s in c_res.steps:
        print(f"    - Step {s['step_id']}: {s['action']} [Tool: {s['tool']}] -> Success: {s['success']}")
    print(f"  Generated Artifacts ({len(c_res.artifacts)}):")
    for a in c_res.artifacts:
        print(f"    - {a['filename']} (Type: {a['type']}, SHA256: {a['sha256'][:16]}..., Verified: {a['verified']})")

    # 4. Audit Trail Summary
    print("\n[4/5] AUDIT TRAIL SUMMARY:")
    all_events = audit_service.get_all_events()
    print(f"  Total Audit Events Recorded: {len(all_events)}")
    recent_types = [e['event_type'] for e in all_events[-8:]]
    print(f"  Recent Event Types: {recent_types}")

    # 5. Technical Sovereignty Evidence
    print("\n[5/5] TECHNICAL SOVEREIGNTY EVIDENCE SUMMARY:")
    evidence = security_reporter.generate_evidence_report()
    print(json.dumps(evidence["technical_proof_summary"], indent=4))
    print(f"\nFormal Statement: {evidence['formal_statement']}")
    print("=" * 70)

if __name__ == "__main__":
    main()
