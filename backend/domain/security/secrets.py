import re
import logging
from typing import Set

class SecretRegistry:
    """Central registry for sensitive strings that must be redacted from logs and events."""

    def __init__(self):
        self._secrets: Set[str] = set()
        self._pattern: re.Pattern | None = None

    def register(self, secret: str) -> None:
        """Register a new secret string for redaction. Recompiles the regex pattern."""
        if not secret or len(secret) < 3:
            # Don't redact tiny strings, it causes false positives
            return

        self._secrets.add(secret)
        self._compile_pattern()

    def _compile_pattern(self) -> None:
        """Compile a combined regex pattern for all registered secrets."""
        if not self._secrets:
            self._pattern = None
            return

        # Escape secrets and join them into a single regex (e.g. 'secret1|secret2')
        escaped_secrets = [re.escape(s) for s in sorted(self._secrets, key=len, reverse=True)]
        self._pattern = re.compile("|".join(escaped_secrets))

    def redact(self, text: str) -> str:
        """Replaces any registered secrets in the given text with ***REDACTED***."""
        if not text or not self._pattern:
            return text

        return self._pattern.sub("***REDACTED***", text)

# Global registry instance
registry = SecretRegistry()

class SecretRedactionFilter(logging.Filter):
    """
    Standard library logging filter that redacts secrets from all log messages.
    Usage: logger.addFilter(SecretRedactionFilter())
    """
    def filter(self, record: logging.LogRecord) -> bool:
        # Pre-format the message entirely to catch strings hidden inside
        # objects, dicts, etc., that the logger itself will stringify.
        # This replaces the native lazy formatting but ensures perfect redaction.
        try:
            original_msg = record.getMessage()
            record.msg = registry.redact(original_msg)
            record.args = () # Clear args since we already formatted
        except Exception:
            # If getMessage fails, fall back to basic string redaction
            if isinstance(record.msg, str):
                record.msg = registry.redact(record.msg)

        return True

def setup_global_log_redaction():
    """Applies the secret redaction filter to the root logger."""
    root_logger = logging.getLogger()
    redactor = SecretRedactionFilter()
    for handler in root_logger.handlers:
        handler.addFilter(redactor)
