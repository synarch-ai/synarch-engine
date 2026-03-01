import re
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
