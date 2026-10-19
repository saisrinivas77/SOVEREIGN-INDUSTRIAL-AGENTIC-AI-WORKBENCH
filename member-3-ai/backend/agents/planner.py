"""Structured Agent Planner.

Conforms strictly to MASTER/06_AGENT_CONTRACT.md and MASTER/14_PROMPT_ENGINEERING_CONTRACT.md.
Produces bounded, canonical AgentPlan objects using registered tools.
"""

from typing import List, Optional
from ..models.base import ModelAdapter
from ..models.schemas import AgentPlan, PlanStep, Task, TaskType
from .bounds import MAX_STEPS
from .injection_defense import PromptSanitizer

ALLOWED_TOOLS = [
    "read_file",
    "search_knowledge",
    "analyze_image",
    "run_python",
    "create_docx",
    "create_xlsx",
    "calculator"
]


class AgentPlanner:
    """Generates structured AgentPlan conforming to canonical schema."""

    def __init__(self, model_adapter: Optional[ModelAdapter] = None):
        self.model_adapter = model_adapter

    def create_plan(
        self,
        task: Task,
        task_type: TaskType,
        files: Optional[List[str]] = None
    ) -> AgentPlan:
        """Create structured execution plan for the given task."""
        file_list = files or task.file_ids

        # If model adapter is available, attempt structured generation with fallback
        if self.model_adapter:
            try:
                from ..models.schemas import ModelMessage, ModelRequest
                prompt = (
                    f"Create an execution plan for this task:\n"
                    f"Task ID: {task.task_id}\n"
                    f"Instruction: {task.instruction}\n"
                    f"Files: {file_list}\n"
                    f"Task Type: {task_type}\n"
                    f"Allowed tools: {ALLOWED_TOOLS}\n"
                    f"Maximum steps allowed: {MAX_STEPS}."
                )
                req = ModelRequest(
                    messages=[
                        ModelMessage(role="system", content="You are the local task planner. Return ONLY valid JSON matching AgentPlan schema."),
                        ModelMessage(role="user", content=prompt)
                    ],
                    temperature=0.0
                )
                plan, _ = self.model_adapter.structured_generate(req, AgentPlan)
                
                # Sanitize and validate tools in the generated plan
                return self._validate_and_sanitize_plan(plan, task.task_id)
            except Exception:
                # Controlled deterministic plan fallback
                pass

        return self._generate_deterministic_plan(task, task_type, file_list)

    def _validate_and_sanitize_plan(self, plan: AgentPlan, task_id: str) -> AgentPlan:
        """Ensure all steps adhere to tool policy and step bounds."""
        sanitized_steps: List[PlanStep] = []
        
        for idx, step in enumerate(plan.steps[:MAX_STEPS], start=1):
            tool = step.tool
            if tool and tool not in ALLOWED_TOOLS:
                tool = None  # Neutralize hallucinated tool
            
            sanitized_steps.append(PlanStep(
                step_id=idx,
                action=step.action,
                tool=tool,
                expected_output=step.expected_output
            ))

        if not sanitized_steps:
            sanitized_steps.append(PlanStep(
                step_id=1,
                action="Analyze request and synthesize response",
                tool=None,
                expected_output="Direct analysis synthesis"
            ))

        return AgentPlan(
            task_id=task_id,
            goal=plan.goal or "Execute requested task",
            steps=sanitized_steps
        )

    def _generate_deterministic_plan(
        self,
        task: Task,
        task_type: TaskType,
        files: List[str]
    ) -> AgentPlan:
        """Deterministic plan templates for high-reliability local execution."""
        steps: List[PlanStep] = []

        # 1. Multi-modal / Inspection Workflow (Golden Workflow)
        has_image = any(f.lower().endswith((".jpg", ".png", ".jpeg", ".tiff")) for f in files)
        has_pdf = any(f.lower().endswith(".pdf") for f in files)
        has_csv = any(f.lower().endswith((".csv", ".tsv")) for f in files)

        if (task_type == "document" and has_image) or (has_pdf and has_image):
            steps.append(PlanStep(
                step_id=1,
                action="Read inspection report and extract technical findings",
                tool="read_file",
                expected_output="Inspection report findings"
            ))
            steps.append(PlanStep(
                step_id=2,
                action="Retrieve relevant standard operating procedure (SOP) guidelines",
                tool="search_knowledge",
                expected_output="Relevant SOP sections with citations"
            ))
            steps.append(PlanStep(
                step_id=3,
                action="Analyze inspection photograph for physical defects and corrosion",
                tool="analyze_image",
                expected_output="Visual defect classification and severity assessment"
            ))
            steps.append(PlanStep(
                step_id=4,
                action="Synthesize all evidence and generate approval note document",
                tool="create_docx",
                expected_output="Verified approval_note.docx artifact"
            ))

        # 2. Coding / Data Analysis Workflow (Second Demo)
        elif task_type == "coding" or has_csv:
            steps.append(PlanStep(
                step_id=1,
                action="Read and inspect data structure of input dataset",
                tool="read_file",
                expected_output="Data schema and column summary"
            ))
            steps.append(PlanStep(
                step_id=2,
                action="Execute sandboxed Python analysis to process dataset and compute metrics",
                tool="run_python",
                expected_output="Statistical analysis results and anomaly indicators"
            ))
            steps.append(PlanStep(
                step_id=3,
                action="Generate structured Excel spreadsheet with summary metrics",
                tool="create_xlsx",
                expected_output="Verified results.xlsx artifact"
            ))

        # 3. Pure Document / RAG Workflow
        elif task_type == "document":
            steps.append(PlanStep(
                step_id=1,
                action="Read input document",
                tool="read_file",
                expected_output="Document content"
            ))
            steps.append(PlanStep(
                step_id=2,
                action="Retrieve supporting procedural guidelines from knowledge base",
                tool="search_knowledge",
                expected_output="Grounded citations"
            ))
            steps.append(PlanStep(
                step_id=3,
                action="Synthesize report and generate output document",
                tool="create_docx",
                expected_output="Verified output.docx artifact"
            ))

        # 4. Pure Vision Workflow
        elif task_type == "vision":
            steps.append(PlanStep(
                step_id=1,
                action="Analyze image for structural defects and engineering specifications",
                tool="analyze_image",
                expected_output="Structured visual observation"
            ))
            steps.append(PlanStep(
                step_id=2,
                action="Synthesize findings and generate inspection report",
                tool="create_docx",
                expected_output="Verified inspection_summary.docx artifact"
            ))

        # 5. General Reasoning Fallback
        else:
            steps.append(PlanStep(
                step_id=1,
                action="Analyze request and synthesize evidence-grounded response",
                tool=None,
                expected_output="Synthesized response"
            ))

        return AgentPlan(
            task_id=task.task_id,
            goal=f"Execute {task_type} task: {task.instruction[:80]}",
            steps=steps
        )
