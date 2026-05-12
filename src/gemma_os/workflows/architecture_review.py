"""
Architecture Review Workflow - System design evaluation and recommendations
"""

from typing import Dict, Any
from pathlib import Path

from .base import BaseWorkflow
from ..core import Config


class ArchitectureReviewWorkflow(BaseWorkflow):
    """
    Architecture review workflow for system design evaluation.

    Assesses:
    - Scalability (vertical/horizontal)
    - Reliability & fault tolerance
    - Technology choices
    - Data architecture
    - API design
    - Security architecture
    - Operational concerns
    """

    REVIEW_DIMENSIONS = [
        "scalability",
        "reliability",
        "technology",
        "data_architecture",
        "api_design",
        "security",
        "operations",
    ]

    def __init__(self, config: Config = None):
        super().__init__(config=config)
        self.skill_name = "architecture-review"

    def validate_inputs(self, **kwargs) -> bool:
        """Validate architecture review inputs"""
        # Require design document or architecture description
        if not kwargs.get("design_file") and not kwargs.get("description"):
            print("✗ Error: Provide --design-file or --description parameter")
            return False

        # Validate file exists if provided
        if kwargs.get("design_file"):
            design_path = Path(kwargs["design_file"]).expanduser()
            if not design_path.exists():
                print(f"✗ Error: Design file not found: {design_path}")
                return False

        # Validate depth parameter
        depth = kwargs.get("depth", "comprehensive")
        valid_depths = ["quick", "standard", "comprehensive"]
        if depth not in valid_depths:
            print(f"✗ Error: Invalid depth. Use: {', '.join(valid_depths)}")
            return False

        return True

    def prepare_context(self, **kwargs) -> Dict[str, Any]:
        """Prepare context for architecture review"""
        context = {
            "review_type": "system_architecture",
            "depth": kwargs.get("depth", "comprehensive"),
            "focus_dimensions": kwargs.get("focus", "all").split(","),
        }

        # Read design document if provided
        if kwargs.get("design_file"):
            design_path = Path(kwargs["design_file"]).expanduser()
            with open(design_path, 'r') as f:
                context["design_content"] = f.read()
            context["design_filename"] = design_path.name

        # Or use provided description
        elif kwargs.get("description"):
            context["design_description"] = kwargs["description"]

        # Add technology stack if provided
        if kwargs.get("tech_stack"):
            context["technology_stack"] = kwargs["tech_stack"].split(",")

        return context

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute architecture review"""
        result = super().execute(**kwargs)

        if result["status"] == "completed":
            result["workflow_type"] = "architecture_review"
            result["review_summary"] = {
                "dimensions_reviewed": len(result.get("focus_dimensions", [])),
                "overall_score": 0.0,
                "recommendations_count": 0,
                "risk_areas": [],
            }

        return result
