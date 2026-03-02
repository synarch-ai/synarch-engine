import contextvars
from typing import Optional

# Global context variable for the current actor/user
current_actor: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("current_actor", default=None)

def set_actor(actor: str) -> contextvars.Token:
    """Sets the current actor and returns the context token."""
    return current_actor.set(actor)

def get_actor() -> str:
    """Gets the current actor. Defaults to 'system' if not set."""
    actor = current_actor.get()
    return actor if actor else "system"

def reset_actor(token: contextvars.Token) -> None:
    """Resets the actor context using the provided token."""
    current_actor.reset(token)
