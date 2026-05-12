"""Base workflow class for common task patterns"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from ..core import (
    ModelRouter,
    Orchestrator,
    Database,
    Config,
)
from ..knowledge import GraphQuery


class BaseWorkflow:
    """Base class for all workflows"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.router = ModelRouter(config=self.config)
        self.orchestrator = Orchestrator(config=self.config)
        self.database = Database(config=self.config)
        self.graph_query = GraphQuery()
        self.task_id = str(uuid.uuid4())[:8]

    def validate_inputs(self, **kwargs) -> bool:
        """Validate workflow inputs. Override in subclasses."""
        return True

    def prepare_context(self, **kwargs) -> Dict[str, Any]:
        """Prepare context for agent execution. Override in subclasses."""
        return {}

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the workflow.

        Returns:
            Dictionary with results and metadata
        """
        # Initialize task in database
        self.database.init()
        self.database.create_task(
            task_id=self.task_id,
            task_name=self.__class__.__name__,
            task_type="workflow",
            input_data=kwargs,
        )

        # Log workflow start
        self.database.log_audit(
            task_id=self.task_id,
            event_type="workflow_started",
            event_data={"workflow": self.__class__.__name__},
        )

        try:
            # Validate inputs
            if not self.validate_inputs(**kwargs):
                raise ValueError("Input validation failed")

            # Analyze task complexity
            task_description = kwargs.get("task", "")
            model, analysis = self.router.select_model(task_description)

            # Log model selection
            self.database.log_audit(
                task_id=self.task_id,
                event_type="model_selected",
                event_data={
                    "model": model,
                    "reasoning": analysis.reasoning,
                    "complexity": analysis.reasoning_depth,
                },
            )

            # Prepare context
            context = self.prepare_context(**kwargs)

            # Enrich context with knowledge graph (related tasks and entities)
            task_description = kwargs.get("task", "")
            if task_description:
                try:
                    related_tasks = self.graph_query.find_related_tasks(
                        self.task_id,
                        max_hops=2,
                        limit=3
                    )
                    if related_tasks:
                        context['related_tasks'] = related_tasks
                except Exception:
                    pass  # Knowledge graph not initialized yet, skip enrichment

            # Create workflow tasks
            tasks = self.orchestrator.create_workflow(
                task_name=kwargs.get("task", "Unknown task")
            )

            # Execute tasks
            results = self.orchestrator.execute_tasks(context=context)

            # Compile results
            workflow_output = {
                "task_id": self.task_id,
                "status": "completed",
                "workflow": self.__class__.__name__,
                "model_selected": model,
                "results": [r.to_dict() for r in results],
                "execution_log": self.orchestrator.get_execution_log(),
            }

            # Update task in database
            self.database.update_task(
                task_id=self.task_id,
                status="completed",
                output_data=workflow_output,
                model_selected=model,
                routing_reason=analysis.reasoning,
            )

            # Log completion
            self.database.log_audit(
                task_id=self.task_id,
                event_type="workflow_completed",
                event_data={"status": "success"},
            )

            return workflow_output

        except Exception as e:
            # Log error
            self.database.log_audit(
                task_id=self.task_id,
                event_type="workflow_error",
                event_data={"error": str(e)},
                severity="ERROR",
            )

            # Update task status
            self.database.update_task(
                task_id=self.task_id,
                status="failed",
                output_data={"error": str(e)},
            )

            return {
                "task_id": self.task_id,
                "status": "error",
                "error": str(e),
            }

    def get_audit_log(self) -> list:
        """Retrieve audit log for this workflow execution"""
        return self.database.get_audit_log(self.task_id)

    def cleanup(self):
        """Cleanup database connections"""
        self.database.close()
