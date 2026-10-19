"""
Sandbox Security Policy & AST Code Analyzer.
Performs static analysis to detect forbidden modules, network calls,
system commands, and unauthorized file access attempts before execution.
"""

import ast
from typing import List, Tuple, Set

class SandboxSecurityViolation(PermissionError):
    """Raised when Python code submitted to the sandbox violates security constraints."""
    pass

class SandboxPolicy:
    """
    Defines and checks security rules for sandboxed code execution.
    """

    # Modules strictly prohibited inside the sandbox
    FORBIDDEN_MODULES: Set[str] = {
        "socket",
        "urllib",
        "urllib3",
        "requests",
        "http",
        "httpx",
        "aiohttp",
        "ftplib",
        "telnetlib",
        "smtplib",
        "imaplib",
        "poplib",
        "subprocess",
        "pty",
        "ctypes",
        "multiprocessing",
        "threading",
        "winreg",
        "msvcrt",
        "posix",
    }

    # Forbidden attribute access / builtins
    FORBIDDEN_CALLS: Set[str] = {
        "eval",
        "exec",
        "compile",
        "__import__",
        "breakpoint",
        "system",
        "popen",
        "spawn",
        "fork",
        "kill",
    }

    # Forbidden sensitive file targets in code strings
    SENSITIVE_TARGETS: List[str] = [
        ".env",
        "id_rsa",
        "id_ed25519",
        "known_hosts",
        "authorized_keys",
        "/etc/passwd",
        "/etc/shadow",
        "C:\\Windows",
        "C:/Windows",
        "System32",
        "docker.sock"
    ]

    def analyze_code(self, code_str: str) -> Tuple[bool, List[str]]:
        """
        Analyze code AST and string contents for security violations.
        Returns (is_safe: bool, violations: List[str]).
        """
        violations: List[str] = []

        # 1. String-level sensitive keyword scan
        for target in self.SENSITIVE_TARGETS:
            if target.lower() in code_str.lower():
                violations.append(f"Attempted access to forbidden host secret or system target: '{target}'")

        # 2. AST parsing & inspection
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            # Syntax errors will be reported upon execution, but AST check passes
            return True, []

        for node in ast.walk(tree):
            # Check import statements (e.g. import socket)
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_pkg = alias.name.split(".")[0]
                    if root_pkg in self.FORBIDDEN_MODULES:
                        violations.append(f"Forbidden module import: '{alias.name}'")

            # Check from ... import statements (e.g. from urllib.request import urlopen)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_pkg = node.module.split(".")[0]
                    if root_pkg in self.FORBIDDEN_MODULES:
                        violations.append(f"Forbidden module import: '{node.module}'")

            # Check function calls (e.g. os.system, eval, exec)
            elif isinstance(node, ast.Call):
                # Direct call e.g. eval()
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.FORBIDDEN_CALLS:
                        violations.append(f"Forbidden function call: '{node.func.id}()'")
                # Attribute call e.g. os.system()
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.FORBIDDEN_CALLS:
                        violations.append(f"Forbidden method call: '.{node.func.attr}()'")

        return (len(violations) == 0), violations

    def validate_code_or_raise(self, code_str: str) -> None:
        """
        Analyze code and raise SandboxSecurityViolation if unsafe.
        """
        is_safe, violations = self.analyze_code(code_str)
        if not is_safe:
            raise SandboxSecurityViolation(
                f"Sandbox Security Violation: {'; '.join(violations)}"
            )

# Global policy instance
sandbox_policy = SandboxPolicy()
