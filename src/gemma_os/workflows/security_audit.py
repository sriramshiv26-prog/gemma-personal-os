"""
Security Audit Workflow - Code vulnerability detection and remediation
"""

from typing import Dict, Any, Optional
import os
from pathlib import Path

from .base import BaseWorkflow
from ..core import Config


class SecurityAuditWorkflow(BaseWorkflow):
    """
    Security auditing workflow for code vulnerability detection.

    Analyzes code for:
    - SQL injection
    - XSS vulnerabilities
    - Authentication/authorization issues
    - Cryptography weaknesses
    - Dependency vulnerabilities
    """

    def __init__(self, config: Config = None):
        super().__init__(config=config)
        self.skill_name = "security-auditing"

    def validate_inputs(self, **kwargs) -> bool:
        """Validate security audit inputs"""
        # Require either file or code
        if not kwargs.get("file") and not kwargs.get("code"):
            print("✗ Error: Provide --file or --code parameter")
            return False

        # Validate file exists if provided
        if kwargs.get("file"):
            file_path = Path(kwargs["file"]).expanduser()
            if not file_path.exists():
                print(f"✗ Error: File not found: {file_path}")
                return False

            # Check file type
            supported_types = {".py", ".js", ".ts", ".java", ".go", ".rs", ".php"}
            if file_path.suffix not in supported_types:
                print(f"✗ Error: Unsupported file type: {file_path.suffix}")
                return False

        return True

    def prepare_context(self, **kwargs) -> Dict[str, Any]:
        """Prepare context for security audit"""
        context = {
            "audit_type": "code_review",
            "severity_threshold": kwargs.get("severity", "Medium"),
            "focus_areas": kwargs.get("focus", "all"),
        }

        # Read file if provided
        if kwargs.get("file"):
            file_path = Path(kwargs["file"]).expanduser()
            with open(file_path, 'r') as f:
                context["code_content"] = f.read()
            context["filename"] = file_path.name

        # Or use provided code
        elif kwargs.get("code"):
            context["code_content"] = kwargs["code"]
            context["filename"] = "stdin"

        return context

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute security audit"""
        result = super().execute(**kwargs)

        # Add security-specific processing
        if result["status"] == "completed":
            result["workflow_type"] = "security_audit"
            result["findings_summary"] = {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            }

        return result
