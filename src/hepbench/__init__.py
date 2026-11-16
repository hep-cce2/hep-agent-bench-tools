"""Grader helpers for hep-agent-bench tasks (https://github.com/hep-cce2/hep-agent-bench-rubric)."""

from .results import write_result
from .scoring import gated_reward, log_gain_vs_expert
from .timing import median_time

RUBRIC_VERSION = "0.2"
__version__ = "0.2.0"
__all__ = ["RUBRIC_VERSION", "gated_reward", "log_gain_vs_expert", "median_time", "write_result"]
