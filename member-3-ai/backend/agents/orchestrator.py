"""LangGraph / State Machine Agent Orchestrator.

Conforms strictly to MASTER/01_MASTER_ARCHITECTURE.md, MASTER/04_DATA_SCHEMAS.md,
MASTER/06_AGENT_CONTRACT.md, and MASTER/09_SECURITY_SOVEREIGNTY.md.

Implements the bounded canonical lifecycle:
INTAKE → CLASSIFY → PLAN → ROUTE → EXECUTE → OBSERVE → VERIFY → NEXT_STEP → COMPLETE
"""

import time
from typing import Any, Callable, Dict, List, Optional
from ..models.base import ModelAdapter
from ..models.registry import ModelRegistry
from ..models.router import ModelRouter
from ..models.schemas import (
    AgentPlan,
    AgentStep,
    ModelSelection,
    Task,
    TaskType,
    get_utc_timestamp,
)
from .bounds import BoundsChecker, BoundedExecutionError, MAX_STEPS
from .classifier import TaskClassifier
from .executor import StepExecutor
from .planner import AgentPlanner
from .state import AgentState
from .verifier import StepVerifier


class AgentOrchestrator:
    """Bounded, auditable, multi-model state machine agent orchestrator."""

    def __init__(
        self,
        router: Optional[ModelRouter] = None,
        executor: Optional[StepExecutor] = None,
        planner: Optional[AgentPlanner] = None,
        workspace_root: Optional[str] = None
    ):
        self.router = router or ModelRouter()
        self.executor = executor or StepExecutor()
        self.planner = planner or AgentPlanner()
        self.workspace_root = workspace_root

    def run(
        self,
        task_id: str,
        instruction: str,
        file_ids: Optional[List[str]] = None,
        task_type_override: Optional[TaskType] = None
    ) -> AgentState:
        """Execute the full bounded agent lifecycle."""
        # 1. INTAKE
        state = self._intake(task_id, instruction, file_ids or [])
        bounds = BoundsChecker()

        try:
            # 2. CLASSIFY
            self._classify(state, task_type_override)

            # 3. PLAN
            self._plan(state)

            # 4. ROUTE MODEL
            self._route(state)

            # 5. EXECUTION & VERIFICATION LOOP
            while state.current_step_index < len(state.plan.steps):
                bounds.check_step_limit(state)
                bounds.check_timeout(state)
                bounds.detect_loops(state)

                current_plan_step = state.plan.steps[state.current_step_index]
                state.step_count += 1

                # EXECUTE & OBSERVE
                executed_step = self.executor.execute_step(current_plan_step, state)

                # VERIFY
                ver_res = StepVerifier.verify_step(executed_step, state, self.workspace_root)
                state.log_trace(
                    f"Verification for Step {executed_step.step_id}: "
                    f"{'PASSED' if ver_res.verified else 'FAILED'} ({ver_res.details})"
                )

                # Handle Step Retries if Failed
                if not ver_res.verified:
                    tool_key = executed_step.tool or "none"
                    retries = state.tool_retries.get(tool_key, 0)
                    if retries < bounds.max_tool_retries:
                        state.tool_retries[tool_key] = retries + 1
                        state.log_trace(f"Retrying Step {executed_step.step_id} (Attempt {retries + 1}/{bounds.max_tool_retries})")
                        continue  # Retry same step
                    else:
                        state.log_trace(f"Step {executed_step.step_id} failed after {retries} retries.")

                # NEXT_STEP
                state.current_step_index += 1

            # 6. COMPLETE
            self._complete(state)

        except BoundedExecutionError as b_err:
            state.status = "failed"
            state.error = f"Bounded execution limit reached: {b_err}"
            state.log_trace(f"EXECUTION TERMINATED: {b_err}")
            state.record_audit(
                event_type="security",
                actor="agent",
                component="AgentOrchestrator",
                status="failure",
                metadata={"error": str(b_err)}
            )
        except Exception as e:
            state.status = "failed"
            state.error = str(e)
            state.log_trace(f"EXECUTION ERROR: {e}")
            state.record_audit(
                event_type="task",
                actor="agent",
                component="AgentOrchestrator",
                status="failure",
                metadata={"error": str(e)}
            )

        return state

    def _intake(self, task_id: str, instruction: str, file_ids: List[str]) -> AgentState:
        """Lifecycle Node: INTAKE"""
        state = AgentState(
            task_id=task_id,
            instruction=instruction,
            file_ids=file_ids,
            status="running"
        )
        state.log_trace(f"Task {task_id} received. INTAKE initialized.")
        state.record_audit(
            event_type="task",
            actor="user",
            component="AgentOrchestrator",
            status="success",
            metadata={"instruction": instruction, "file_count": len(file_ids)}
        )
        return state

    def _classify(self, state: AgentState, override: Optional[TaskType]) -> None:
        """Lifecycle Node: CLASSIFY"""
        if override:
            t_type = override
            cap, _, reason = self.router.determine_capability(state.instruction, state.file_ids, t_type)
        else:
            t_type, cap, reason = TaskClassifier.classify(state.instruction, state.file_ids)

        state.task_type = t_type
        state.log_trace(f"Classification completed: TaskType={t_type}, RequiredCapability={cap}. Reason: {reason}")
        state.record_audit(
            event_type="task",
            actor="agent",
            component="TaskClassifier",
            status="success",
            metadata={"task_type": t_type, "required_capability": cap, "reason": reason}
        )

    def _plan(self, state: AgentState) -> None:
        """Lifecycle Node: PLAN"""
        task_obj = Task(
            task_id=state.task_id,
            instruction=state.instruction,
            file_ids=state.file_ids,
            task_type=state.task_type,
            status="running"
        )
        plan = self.planner.create_plan(task_obj, state.task_type, state.file_ids)
        state.plan = plan
        state.log_trace(f"Plan generated with {len(plan.steps)} bounded steps. Goal: {plan.goal}")
        state.record_audit(
            event_type="task",
            actor="agent",
            component="AgentPlanner",
            status="success",
            metadata={"goal": plan.goal, "step_count": len(plan.steps)}
        )

    def _route(self, state: AgentState) -> None:
        """Lifecycle Node: ROUTE"""
        model_sel = self.router.select_model(
            instruction=state.instruction,
            file_ids=state.file_ids,
            task_type=state.task_type
        )
        state.active_model_selection = model_sel
        state.log_trace(
            f"Model routed: model_id='{model_sel.model_id}', capability='{model_sel.capability}', "
            f"confidence={model_sel.confidence}. Reason: {model_sel.reason}"
        )
        state.record_audit(
            event_type="model_call",
            actor="agent",
            component="ModelRouter",
            status="success",
            metadata={
                "model_id": model_sel.model_id,
                "capability": model_sel.capability,
                "reason": model_sel.reason
            }
        )

    def _complete(self, state: AgentState) -> None:
        """Lifecycle Node: COMPLETE"""
        state.status = "completed"
        state.updated_at = get_utc_timestamp()
        state.log_trace(f"Task {state.task_id} completed successfully. Artifacts: {len(state.artifacts)}, Sources: {len(state.sources)}.")
        state.record_audit(
            event_type="task",
            actor="agent",
            component="AgentOrchestrator",
            status="success",
            metadata={
                "steps_executed": len(state.steps),
                "artifacts_count": len(state.artifacts),
                "sources_count": len(state.sources)
            }
        )
