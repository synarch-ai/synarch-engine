"""Domain exceptions for orchestration runtime."""


class BudgetExceededError(RuntimeError):
    """Raised when mission execution exceeds the configured model-call budget."""



class ResultPersistError(RuntimeError):
    """Raised when a finished mission's result could not be stored after retries."""


class CheckpointReadError(RuntimeError):
    """Raised when a mission's durable checkpoint could not be read after retries."""
