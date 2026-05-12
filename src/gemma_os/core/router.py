"""
Model Router - Intelligent routing between Gemma 4 26B and 2B models

Routes tasks to optimal model based on complexity analysis.
"""

from typing import Tuple, Literal
from dataclasses import dataclass
import ollama

from .config import Config


@dataclass
class ComplexityAnalysis:
    """Result of complexity analysis"""
    input_tokens: int
    estimated_output_tokens: int
    reasoning_depth: Literal["simple", "moderate", "complex"]
    requires_external_apis: bool
    context_needed: bool
    selected_model: str
    reasoning: str


class ModelRouter:
    """Route tasks to optimal model (26B expert or 2B fast)"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.client = ollama.Client(host=self.config.ollama.host)
        self.expert_model = self.config.ollama.model_expert
        self.fast_model = self.config.ollama.model_fast
        self.threshold = self.config.ollama.complexity_threshold

    def analyze_complexity(self, task: str) -> ComplexityAnalysis:
        """
        Analyze task complexity to determine optimal model.

        Factors considered:
        - Token count (input length)
        - Reasoning depth indicators (questions, analysis, etc.)
        - Context requirements (mentions of files, documents)
        - External API needs (search, lookup, etc.)
        """

        # Token estimation (rough)
        input_tokens = len(task.split()) * 1.3  # ~1.3 tokens per word

        # Reasoning depth detection
        complex_indicators = [
            "analyze", "compare", "evaluate", "design", "architect",
            "recommend", "trade-off", "refactor", "security", "compliance",
            "multi-step", "reasoning", "explain why", "deep dive"
        ]

        moderate_indicators = [
            "review", "check", "summarize", "explain", "what is",
            "how does", "list", "describe", "example"
        ]

        task_lower = task.lower()
        complex_score = sum(1 for indicator in complex_indicators if indicator in task_lower)
        moderate_score = sum(1 for indicator in moderate_indicators if indicator in task_lower)

        # Determine reasoning depth
        if complex_score >= 2:
            reasoning_depth = "complex"
        elif moderate_score >= 2 or input_tokens > self.threshold:
            reasoning_depth = "moderate"
        else:
            reasoning_depth = "simple"

        # Check for external API needs
        external_api_indicators = ["search", "lookup", "current", "latest", "real-time", "web"]
        requires_external_apis = any(indicator in task_lower for indicator in external_api_indicators)

        # Check for context needs
        context_indicators = ["document", "code", "file", "codebase", "pdf", "project"]
        context_needed = any(indicator in task_lower for indicator in context_indicators)

        # Model selection logic
        if reasoning_depth == "complex" or (moderate_score >= 2 and input_tokens > self.threshold):
            selected_model = self.expert_model
            reasoning = f"Complex reasoning required (indicators: {complex_score}, tokens: {input_tokens:.0f})"
        elif reasoning_depth == "moderate" and input_tokens > self.threshold:
            selected_model = self.expert_model
            reasoning = f"Moderate reasoning + large context (tokens: {input_tokens:.0f})"
        else:
            selected_model = self.fast_model
            reasoning = f"Simple task (reasoning_depth: {reasoning_depth}, tokens: {input_tokens:.0f})"

        # Estimated output tokens (rough heuristic)
        if reasoning_depth == "complex":
            estimated_output_tokens = int(input_tokens * 2.5)  # More reasoning = more output
        elif reasoning_depth == "moderate":
            estimated_output_tokens = int(input_tokens * 1.5)
        else:
            estimated_output_tokens = int(input_tokens * 0.8)

        return ComplexityAnalysis(
            input_tokens=int(input_tokens),
            estimated_output_tokens=estimated_output_tokens,
            reasoning_depth=reasoning_depth,
            requires_external_apis=requires_external_apis,
            context_needed=context_needed,
            selected_model=selected_model,
            reasoning=reasoning,
        )

    def select_model(self, task: str) -> Tuple[str, ComplexityAnalysis]:
        """
        Select optimal model for task.

        Returns:
            Tuple of (model_name, analysis)
        """
        analysis = self.analyze_complexity(task)
        return analysis.selected_model, analysis

    def health_check(self) -> dict:
        """Check model availability and health"""
        try:
            tags = self.client.list()
            models = [tag['name'] for tag in tags['models']]

            expert_available = self.expert_model in models
            fast_available = self.fast_model in models

            return {
                "status": "healthy" if expert_available and fast_available else "degraded",
                "expert_model": {
                    "name": self.expert_model,
                    "available": expert_available,
                },
                "fast_model": {
                    "name": self.fast_model,
                    "available": fast_available,
                },
                "all_models": models,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to connect to Ollama",
            }

    def test_inference(self, model: str = None) -> dict:
        """Test inference on specified or default model"""
        model = model or self.fast_model

        try:
            response = self.client.generate(
                model=model,
                prompt="Hello! Test inference.",
                stream=False,
            )

            return {
                "status": "success",
                "model": model,
                "inference_time_ms": response.get("total_duration", 0) // 1_000_000,
                "tokens_per_second": response.get("eval_count", 0) / (response.get("eval_duration", 1) / 1e9),
            }
        except Exception as e:
            return {
                "status": "error",
                "model": model,
                "error": str(e),
            }
