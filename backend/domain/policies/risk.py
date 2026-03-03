"""Risk policy domain logic."""
from enum import Enum
from typing import Any


class RiskLevel(str, Enum):
    LOW = "low"        # e.g., read-only, harmless
    MEDIUM = "medium"  # e.g., standard generation
    HIGH = "high"      # e.g., code execution, file write, external API
    CRITICAL = "critical" # e.g., destructive, PII access

class PolicyEvaluator:
    """Evaluates the risk of an action/tool call."""

    @staticmethod
    def evaluate_tool_call(tool_name: str, args: dict[str, Any]) -> RiskLevel:
        """Determine risk level for a given tool call."""

        # Hardcoded policy for Phase 1/S06
        # In future phases, this will be config-driven (S21)

        high_risk_tools = {
            "bash", "python_repl", "write_file", "delete_file",
            "deploy", "http_request"
        }

        if tool_name in high_risk_tools:
            return RiskLevel.HIGH

        if tool_name.startswith("read_"):
            return RiskLevel.LOW

        return RiskLevel.MEDIUM
