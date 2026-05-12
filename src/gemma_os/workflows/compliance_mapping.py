"""
Compliance Mapping Workflow - Regulatory framework mapping and gap analysis
"""

from typing import Dict, Any, List
from pathlib import Path

from .base import BaseWorkflow
from ..core import Config


class ComplianceMappingWorkflow(BaseWorkflow):
    """
    Compliance mapping workflow for framework assessment.

    Supports:
    - GDPR (General Data Protection Regulation)
    - HIPAA (Health Insurance Portability)
    - SOC2 (Service Organization Control)
    - PCI-DSS (Payment Card Industry)
    - ISO 27001 (Information Security Management)
    """

    SUPPORTED_FRAMEWORKS = {
        "GDPR": "General Data Protection Regulation",
        "HIPAA": "Health Insurance Portability & Accountability",
        "SOC2": "Service Organization Control",
        "PCI-DSS": "Payment Card Industry Data Security Standard",
        "ISO27001": "Information Security Management",
    }

    def __init__(self, config: Config = None):
        super().__init__(config=config)
        self.skill_name = "compliance-mapping"

    def validate_inputs(self, **kwargs) -> bool:
        """Validate compliance assessment inputs"""
        frameworks = kwargs.get("frameworks", "").split(",")

        # Validate framework names
        for framework in frameworks:
            framework = framework.strip().upper()
            if framework not in self.SUPPORTED_FRAMEWORKS:
                print(f"✗ Error: Unsupported framework: {framework}")
                print(f"  Supported: {', '.join(self.SUPPORTED_FRAMEWORKS.keys())}")
                return False

        # Require policy document
        if kwargs.get("policy_file"):
            policy_path = Path(kwargs["policy_file"]).expanduser()
            if not policy_path.exists():
                print(f"✗ Error: Policy file not found: {policy_path}")
                return False

        return True

    def prepare_context(self, **kwargs) -> Dict[str, Any]:
        """Prepare context for compliance mapping"""
        frameworks = [f.strip().upper() for f in kwargs.get("frameworks", "").split(",")]

        context = {
            "assessment_type": "gap_analysis",
            "frameworks": frameworks,
            "framework_descriptions": {
                f: self.SUPPORTED_FRAMEWORKS[f] for f in frameworks
            },
        }

        # Read policy document if provided
        if kwargs.get("policy_file"):
            policy_path = Path(kwargs["policy_file"]).expanduser()
            with open(policy_path, 'r') as f:
                context["policy_content"] = f.read()

        return context

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute compliance assessment"""
        result = super().execute(**kwargs)

        if result["status"] == "completed":
            result["workflow_type"] = "compliance_mapping"
            result["assessment_summary"] = {
                "frameworks_assessed": len(result.get("frameworks_assessed", [])),
                "total_requirements": 0,
                "implemented": 0,
                "partial": 0,
                "missing": 0,
                "overall_compliance_percentage": 0,
            }

        return result
