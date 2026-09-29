"""FDE Evaluation Framework for AI Agents & Operational Pipelines.

Evaluates task success rate, schema validity, safety (unauthorized action rate),
p95 latency, cost-per-task, and fallback rate.
"""

from .harness import EvaluationHarness, EvaluationBenchmarkResult, run_eval_suite

__all__ = ["EvaluationHarness", "EvaluationBenchmarkResult", "run_eval_suite"]
