"""Domain exceptions for orchestration runtime."""


class BudgetExceededError(RuntimeError):
    """Raised when mission execution exceeds the configured model-call budget."""

