from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class AgentRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    ANALYST = "analyst"
    RESTRICTED = "restricted"

class PermissionProfile(BaseModel):
    """
    Defines the least-privilege access model for an agent (FR-52).
    """
    role: AgentRole = Field(default=AgentRole.RESTRICTED)

    # Explicit list of tool names the agent is allowed to invoke.
    # If empty, the agent cannot invoke any tools.
    allowed_tools: List[str] = Field(default_factory=list)

    # Fine-grained resource access strings (e.g., 'fs:read:/tmp', 'github:write')
    scopes: List[str] = Field(default_factory=list)

    def can_invoke(self, tool_name: str) -> bool:
        """Check if the agent is explicitly allowed to invoke this tool."""
        if self.role == AgentRole.ADMIN:
            return True # Admins bypass tool whitelist
        return tool_name in self.allowed_tools

    def has_scope(self, required_scope: str) -> bool:
        """
        Check if the agent possesses a specific scope.
        Supports basic wildcard matching (e.g. 'fs:*' matches 'fs:read:/tmp')
        """
        if self.role == AgentRole.ADMIN:
            return True

        for scope in self.scopes:
            if scope == required_scope:
                return True
            if scope.endswith('*'):
                prefix = scope[:-1]
                if required_scope.startswith(prefix):
                    return True
        return False
