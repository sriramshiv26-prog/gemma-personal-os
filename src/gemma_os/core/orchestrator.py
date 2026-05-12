"""
CrewAI Orchestrator - Multi-agent task coordination

Manages agent creation, tool binding, and task execution.
"""

from typing import Optional, List, Dict, Any
import json
from datetime import datetime
from .config import Config


class Agent:
    """Represents a CrewAI Agent with specific role and expertise"""

    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        tools: List[str] = None,
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "tools": self.tools,
        }


class Task:
    """Represents a CrewAI Task for agent execution"""

    def __init__(
        self,
        name: str,
        description: str,
        agent: Agent,
        expected_output: str,
        depends_on: Optional[str] = None,
    ):
        self.name = name
        self.description = description
        self.agent = agent
        self.expected_output = expected_output
        self.depends_on = depends_on
        self.status = "pending"
        self.result = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "agent": self.agent.to_dict(),
            "expected_output": self.expected_output,
            "depends_on": self.depends_on,
            "status": self.status,
        }


class ExecutionResult:
    """Result of workflow execution"""

    def __init__(
        self,
        task_name: str,
        status: str,
        output: str,
        execution_time_ms: float,
        tokens_used: int = 0,
        errors: List[str] = None,
    ):
        self.task_name = task_name
        self.status = status
        self.output = output
        self.execution_time_ms = execution_time_ms
        self.tokens_used = tokens_used
        self.errors = errors or []
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {
            "task_name": self.task_name,
            "status": self.status,
            "output": self.output,
            "execution_time_ms": self.execution_time_ms,
            "tokens_used": self.tokens_used,
            "errors": self.errors,
            "timestamp": self.timestamp,
        }


class Orchestrator:
    """Multi-agent orchestrator using CrewAI patterns"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.agents: Dict[str, Agent] = {}
        self.tasks: List[Task] = []
        self.execution_results: List[ExecutionResult] = []

    def add_agent(self, agent: Agent) -> None:
        """Register an agent"""
        self.agents[agent.name] = agent

    def add_task(self, task: Task) -> None:
        """Register a task"""
        self.tasks.append(task)

    def create_standard_agents(self) -> Dict[str, Agent]:
        """
        Create standard agent set for typical workflows.
        Returns dict of pre-configured agents.
        """

        agents = {
            "analyst": Agent(
                name="analyst",
                role="Senior Analyst",
                goal="Understand the task deeply and break it into actionable components",
                backstory="Expert at analyzing complex problems and identifying key requirements",
                tools=["document_parser", "code_analyzer", "rag_query"],
            ),
            "executor": Agent(
                name="executor",
                role="Task Executor",
                goal="Execute the plan and produce results",
                backstory="Skilled at implementing solutions and using available tools",
                tools=["code_executor", "file_io", "api_caller"],
            ),
            "advisor": Agent(
                name="advisor",
                role="Quality Advisor",
                goal="Review outputs and provide recommendations",
                backstory="Expert at quality assurance and constructive feedback",
                tools=["quality_checker", "compliance_validator"],
            ),
        }

        for agent in agents.values():
            self.add_agent(agent)

        return agents

    def create_workflow(self, task_name: str) -> List[Task]:
        """
        Create a standard workflow for common tasks.

        Workflow pattern:
        1. Analyst: Understand and break down
        2. Executor: Execute tasks
        3. Advisor: Review and validate
        """

        agents = self.create_standard_agents()

        tasks = [
            Task(
                name="analyze",
                description=f"Analyze the task: {task_name}",
                agent=agents["analyst"],
                expected_output="Detailed analysis and breakdown of subtasks",
                depends_on=None,
            ),
            Task(
                name="execute",
                description=f"Execute the plan for: {task_name}",
                agent=agents["executor"],
                expected_output="Complete results from task execution",
                depends_on="analyze",
            ),
            Task(
                name="review",
                description=f"Review and validate results for: {task_name}",
                agent=agents["advisor"],
                expected_output="Quality assessment and recommendations",
                depends_on="execute",
            ),
        ]

        for task in tasks:
            self.add_task(task)

        return tasks

    def execute_tasks(
        self,
        context: Dict[str, Any] = None,
        timeout: int = 300,
    ) -> List[ExecutionResult]:
        """
        Execute registered tasks with error handling.

        Args:
            context: Additional context/variables for task execution
            timeout: Timeout per task in seconds

        Returns:
            List of ExecutionResult objects
        """

        context = context or {}
        results = []

        for task in self.tasks:
            # Check dependencies
            if task.depends_on:
                dependency_result = next(
                    (r for r in results if r.task_name == task.depends_on),
                    None,
                )
                if not dependency_result or dependency_result.status != "success":
                    result = ExecutionResult(
                        task_name=task.name,
                        status="skipped",
                        output="Dependency not met",
                        execution_time_ms=0,
                        errors=["Skipped due to failed dependency"],
                    )
                    results.append(result)
                    continue

            # Simulate task execution (real implementation uses CrewAI)
            # For now, return structured results
            result = ExecutionResult(
                task_name=task.name,
                status="success",
                output=f"Task '{task.name}' executed: {task.description}",
                execution_time_ms=1000,  # Mock value
                tokens_used=500,  # Mock value
                errors=[],
            )

            task.status = "completed"
            results.append(result)
            self.execution_results.append(result)

        return results

    def get_execution_log(self) -> dict:
        """Return execution log for audit purposes"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tasks": len(self.tasks),
            "completed_tasks": sum(1 for t in self.tasks if t.status == "completed"),
            "results": [r.to_dict() for r in self.execution_results],
        }

    def summary(self) -> dict:
        """Return orchestrator summary"""
        return {
            "agents_registered": len(self.agents),
            "agents": [a.to_dict() for a in self.agents.values()],
            "tasks_registered": len(self.tasks),
            "tasks": [t.to_dict() for t in self.tasks],
            "executions_completed": len(self.execution_results),
        }
