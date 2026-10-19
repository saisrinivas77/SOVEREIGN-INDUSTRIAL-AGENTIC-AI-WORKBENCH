"""Bounded Execution Policy & Safeguards.

Conforms strictly to MASTER/06_AGENT_CONTRACT.md.
Enforces step limits, retry limits, loop detection, and timeouts.
"""

from datetime import datetime, timezone
import time
from typing import Dict, List, Optional
from .state import AgentState

# Canonical Contract Constants
MAX_STEPS = 12
MAX_TOOL_RETRIES = 2
MAX_MODEL_RETRIES = 2
TASK_TIMEOUT = 600       # 10 minutes
TOOL_TIMEOUT = 60        # 60 seconds
SANDBOX_TIMEOUT = 30     # 30 seconds


class BoundedExecutionError(Exception):
    """Raised when an execution boundary or limit is violated."""
    pass


class BoundsChecker:
    """Validator that enforces execution boundaries and loop prevention."""

    def __init__(
        self,
        max_steps: int = MAX_STEPS,
        max_tool_retries: int = MAX_TOOL_RETRIES,
        max_model_retries: int = MAX_MODEL_RETRIES,
        task_timeout: int = TASK_TIMEOUT
    ):
        self.max_steps = max_steps
        self.max_tool_retries = max_tool_retries
        self.max_model_retries = max_model_retries
        self.task_timeout = task_timeout
        self.start_monotonic = time.monotonic()

    def check_step_limit(self, state: AgentState) -> None:
        """Enforce MAX_STEPS limit."""
        if state.step_count >= self.max_steps:
            raise BoundedExecutionError(
                f"MAX_STEPS limit ({self.max_steps}) exceeded. Terminating to prevent runaway execution."
            )

    def check_timeout(self, state: AgentState) -> None:
        """Enforce TASK_TIMEOUT limit."""
        elapsed = time.monotonic() - self.start_monotonic
        if elapsed > self.task_timeout:
            raise BoundedExecutionError(
                f"TASK_TIMEOUT ({self.task_timeout}s) exceeded. Execution took {elapsed:.1f}s."
            )

    def check_tool_retries(self, state: AgentState, tool_name: str) -> None:
        """Enforce MAX_TOOL_RETRIES per tool."""
        current_retries = state.tool_retries.get(tool_name, 0)
        if current_retries > self.max_tool_retries:
            raise BoundedExecutionError(
                f"MAX_TOOL_RETRIES ({self.max_tool_retries}) exceeded for tool '{tool_name}'."
            )

    def check_model_retries(self, state: AgentState, model_id: str) -> None:
        """Enforce MAX_MODEL_RETRIES per model."""
        current_retries = state.model_retries.get(model_id, 0)
        if current_retries > self.max_model_retries:
            raise BoundedExecutionError(
                f"MAX_MODEL_RETRIES ({self.max_model_retries}) exceeded for model '{model_id}'."
            )

    def detect_loops(self, state: AgentState) -> None:
        """Detect repeated failed actions or oscillating tool sequences."""
        if len(state.steps) >= 3:
            # Check if last 3 steps were the same action and failed
            last_3 = state.steps[-3:]
            if all(s.status == "failed" for s in last_3):
                actions = [s.action for s in last_3]
                if len(set(actions)) == 1:
                    raise BoundedExecutionError(
                        f"Loop detected: Action '{actions[0]}' failed 3 consecutive times."
                    )
