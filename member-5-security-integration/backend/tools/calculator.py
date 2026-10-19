"""
Calculator Tool (Safe AST Math Evaluator).
Evaluates mathematical expressions safely using an AST evaluator without eval(), exec(),
or code execution vulnerabilities.
"""

import ast
import math
import operator
from typing import Any, Dict, Optional

try:
    from backend.tools.base import BaseTool, ToolResult
    from backend.security.security_manager import security_manager
except ImportError:
    import sys
    from pathlib import Path
    _pkg_root = Path(__file__).resolve().parent.parent.parent
    if str(_pkg_root) not in sys.path:
        sys.path.insert(0, str(_pkg_root))
    from backend.tools.base import BaseTool, ToolResult
    from backend.security.security_manager import security_manager

class SafeMathEvaluator:
    """Safe AST-based math expression evaluator."""

    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    ALLOWED_FUNCTIONS = {
        "sqrt": math.sqrt,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "abs": abs,
        "round": round,
        "ceil": math.ceil,
        "floor": math.floor,
        "min": min,
        "max": max,
    }

    ALLOWED_CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }

    def evaluate(self, expr: str) -> float:
        if not expr or not isinstance(expr, str):
            raise ValueError("Expression must be a non-empty string.")

        # Clean expr
        clean_expr = expr.strip().replace("^", "**")

        try:
            tree = ast.parse(clean_expr, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Invalid math syntax: {str(e)}")

        return self._eval_node(tree.body)

    def _eval_node(self, node: ast.AST) -> Any:
        # Numeric literal
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant value: {node.value}")

        # Named constants (pi, e)
        elif isinstance(node, ast.Name):
            if node.id in self.ALLOWED_CONSTANTS:
                return self.ALLOWED_CONSTANTS[node.id]
            raise ValueError(f"Unknown variable or identifier: '{node.id}'")

        # Binary operator (a + b, a * b, etc.)
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_OPERATORS:
                raise ValueError(f"Unsupported operator: {op_type.__name__}")
            left_val = self._eval_node(node.left)
            right_val = self._eval_node(node.right)
            # Prevent overflow / huge exponent
            if op_type is ast.Pow and (right_val > 1000 or left_val > 100000):
                raise ValueError("Exponentiation magnitude exceeds safe compute limit.")
            return self.ALLOWED_OPERATORS[op_type](left_val, right_val)

        # Unary operator (-x, +x)
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_OPERATORS:
                raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
            operand_val = self._eval_node(node.operand)
            return self.ALLOWED_OPERATORS[op_type](operand_val)

        # Function call (sqrt(x), log(x))
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name not in self.ALLOWED_FUNCTIONS:
                    raise ValueError(f"Forbidden or unsupported function: '{func_name}'")
                arg_vals = [self._eval_node(arg) for arg in node.args]
                return self.ALLOWED_FUNCTIONS[func_name](*arg_vals)
            raise ValueError("Unsupported call structure in expression.")

        raise ValueError(f"Unsupported AST node type: {type(node).__name__}")

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Safely evaluate mathematical and engineering expressions, formulas, and tolerance calculations."
    input_schema = {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Mathematical expression to evaluate (e.g. '(168 - 150) / 150 * 100')"}
        },
        "required": ["expression"]
    }
    permission = "standard"
    timeout_seconds = 10

    def __init__(self):
        self.evaluator = SafeMathEvaluator()

    def execute(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        expression = arguments.get("expression")
        if not expression:
            return ToolResult(
                success=False,
                status="failed",
                error="Missing required argument 'expression'."
            )

        task_id = context.get("task_id") if context else None

        try:
            # Pre-validate for dangerous patterns
            security_manager.validate_tool_invocation("calculator", arguments, task_id=task_id)

            val = self.evaluator.evaluate(expression)
            # Format floating points cleanly
            formatted_val = round(val, 6) if isinstance(val, float) else val

            return ToolResult(
                success=True,
                status="completed",
                result={
                    "expression": expression,
                    "value": formatted_val
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                status="failed",
                error=f"Calculator evaluation failed: {str(e)}"
            )
