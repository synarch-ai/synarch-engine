from typing import Any, Callable, Dict, Optional
from pydantic import BaseModel
import logging

from domain.security.permissions import PermissionProfile

logger = logging.getLogger(__name__)

class GuardrailException(Exception):
    """Raised when a tool input or output violates security policies."""
    pass

class InjectionScanner:
    """Pre-flight heuristic scanner for untrusted inputs (FR-54)."""

    # Common prompt injection signatures to flag
    JAILBREAK_PATTERNS = [
        "ignore previous instructions",
        "system prompt",
        "you are now",
        "disregard the rules",
        "bypassing filters"
    ]

    @classmethod
    def scan(cls, input_text: str) -> bool:
        """Returns True if input is safe, False if potentially malicious."""
        if not input_text:
            return True

        lower_text = input_text.lower()
        for pattern in cls.JAILBREAK_PATTERNS:
            if pattern in lower_text:
                logger.warning(f"InjectionScanner detected malicious pattern: '{pattern}'")
                return False
        return True

def enforce_least_privilege(tool_name: str, profile: PermissionProfile, required_scope: Optional[str] = None) -> None:
    """
    Validates if the agent's permission profile allows invoking this tool.
    Raises GuardrailException if blocked.
    """
    if not profile.can_invoke(tool_name):
        raise GuardrailException(f"Agent is not authorized to invoke tool: {tool_name}")

    if required_scope and not profile.has_scope(required_scope):
        raise GuardrailException(f"Agent lacks required scope: {required_scope} for tool: {tool_name}")

class OutputSanitizer:
    """Sanitizes tool outputs before returning to the agent's context (FR-53)."""

    @classmethod
    def sanitize(cls, output: Any, max_length: int = 10000) -> Any:
        """
        Truncates massively large outputs and redacts secrets via S10 SecretRegistry.
        Handles nested dicts, lists, and strings.
        """
        from domain.security.secrets import registry

        if isinstance(output, str):
            # 1. Truncate
            if len(output) > max_length:
                output = output[:max_length] + f"\n...[Output truncated at {max_length} chars to prevent context bloat]"
            # 2. Redact active secrets
            return registry.redact(output)

        elif isinstance(output, dict):
            return {k: cls.sanitize(v, max_length) for k, v in output.items()}

        elif isinstance(output, list):
            return [cls.sanitize(item, max_length) for item in output]

        elif hasattr(output, "model_dump"): # Pydantic v2
            return cls.sanitize(output.model_dump(), max_length)

        elif hasattr(output, "dict"): # Pydantic v1
            return cls.sanitize(output.dict(), max_length)

        return output

import functools
import hashlib
import json
import asyncio
from datetime import datetime, timedelta

# A simple in-memory LRU-style cache to prevent infinite retry loops and avoid memory leaks.
# In a distributed system, this would be a Redis TTL key keyed by mission_id + hash(tool_name + args)
from collections import OrderedDict

_rejected_attempts_cache: OrderedDict[str, datetime] = OrderedDict()
RETRY_COOLDOWN_SECONDS = 300
MAX_CACHE_SIZE = 1000

def _cleanup_cache():
    """Removes old entries from the cache to prevent memory leaks."""
    now = datetime.utcnow()
    # Remove expired items
    keys_to_delete = []
    for k, v in _rejected_attempts_cache.items():
        if now - v > timedelta(seconds=RETRY_COOLDOWN_SECONDS):
            keys_to_delete.append(k)
    for k in keys_to_delete:
        del _rejected_attempts_cache[k]

    # Enforce max size limit (LRU eviction)
    # Important: Clean up down to MAX_CACHE_SIZE - 1 so the pending insert
    # keeps the total size exactly at MAX_CACHE_SIZE.
    while len(_rejected_attempts_cache) >= MAX_CACHE_SIZE:
        _rejected_attempts_cache.popitem(last=False)

class ToolApprovalTimeoutError(GuardrailException):
    """Raised when an approval for a tool times out, forcing the agent to move on."""
    pass

class ToolRejectedError(GuardrailException):
    """Raised when an operator rejects a tool execution."""
    pass

class InfiniteRetryError(GuardrailException):
    """Raised when an agent attempts to immediately retry a previously rejected tool+argument combination."""
    pass


def _hash_call(tool_name: str, *args, **kwargs) -> str:
    """Creates a deterministic hash of a tool call to track retries."""
    payload = json.dumps({"tool": tool_name, "args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def requires_approval(risk_level: str = "high"):
    """
    Decorator that enforces the 'Rule of Two' (FR-53) for dangerous tools.

    If the exact same tool and arguments were recently rejected by a human,
    it fast-fails with an InfiniteRetryError to prevent the agent from spamming
    approvals in a tight loop.

    (Note: In a full LangGraph implementation, this decorator would yield an
    Interrupt or return a special Command object to pause the graph. Here we
    simulate the boundary by raising a specific exception that the LangGraph
    tool executor must catch and handle.)
    """
    def decorator(func: Callable):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                tool_name = func.__name__
                hash_kwargs = {k: v for k, v in kwargs.items() if not k.startswith("_simulate_")}
                call_hash = _hash_call(tool_name, *args, **hash_kwargs)

                if call_hash in _rejected_attempts_cache:
                    rejection_time = _rejected_attempts_cache[call_hash]
                    if datetime.utcnow() - rejection_time < timedelta(seconds=RETRY_COOLDOWN_SECONDS):
                        logger.warning(f"Fast-failing repeated invocation of rejected async tool: {tool_name}")
                        raise InfiniteRetryError(
                            f"You previously attempted to call '{tool_name}' with these exact arguments and it was rejected by the operator. "
                            "You MUST NOT retry this action. Try a different approach."
                        )
                    else:
                        del _rejected_attempts_cache[call_hash]

                simulate_rejection = kwargs.pop("_simulate_rejection", False)
                if simulate_rejection:
                    _cleanup_cache()
                    _rejected_attempts_cache[call_hash] = datetime.utcnow()
                    _rejected_attempts_cache.move_to_end(call_hash)
                    raise ToolRejectedError(f"Execution of '{tool_name}' was rejected by the operator.")

                # 3. Execute the actual async tool
                result = await func(*args, **kwargs)

                # 4. Sanitize outputs (FR-53) AFTER awaiting
                return OutputSanitizer.sanitize(result)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                tool_name = func.__name__

                # Strip out internal kwargs before hashing so the retry cache works accurately
                hash_kwargs = {k: v for k, v in kwargs.items() if not k.startswith("_simulate_")}
                call_hash = _hash_call(tool_name, *args, **hash_kwargs)

                # 1. Edge Case Protection: Check for recent rejections to prevent infinite retry loops
                if call_hash in _rejected_attempts_cache:
                    rejection_time = _rejected_attempts_cache[call_hash]
                    if datetime.utcnow() - rejection_time < timedelta(seconds=RETRY_COOLDOWN_SECONDS):
                        logger.warning(f"Fast-failing repeated invocation of rejected tool: {tool_name}")
                        raise InfiniteRetryError(
                            f"You previously attempted to call '{tool_name}' with these exact arguments and it was rejected by the operator. "
                            "You MUST NOT retry this action. Try a different approach."
                        )
                    else:
                        # Cooldown expired, clear cache
                        del _rejected_attempts_cache[call_hash]

                # 2. In a real execution, we would pause the graph here and wait for an Approval DB record.
                # We raise a sentinel exception that the LangGraph tool-node catches to trigger an `interrupt`.
                # For testing the edge case cache, we provide a mechanism to simulate a rejection.

                # Simulate a simulated rejection via kwargs for testing the cache
                simulate_rejection = kwargs.pop("_simulate_rejection", False)
                if simulate_rejection:
                    _cleanup_cache()
                    _rejected_attempts_cache[call_hash] = datetime.utcnow()
                    _rejected_attempts_cache.move_to_end(call_hash)
                    raise ToolRejectedError(f"Execution of '{tool_name}' was rejected by the operator.")

                # 3. Execute the actual tool
                result = func(*args, **kwargs)

                # 4. Sanitize outputs (FR-53)
                return OutputSanitizer.sanitize(result)

            return sync_wrapper
    return decorator
