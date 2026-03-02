# S10: Auth Modes, Attribution & Secrets Discipline Design

## Overview
This document outlines the architectural implementation for S10 (Issue #11), addressing the core runtime security fundamentals defined in FR-41 (Gateway Auth), FR-42 (Audit-attribution), and FR-44 (Secrets redaction).

## 1. Authentication Modes (FR-41)
We will introduce a configurable authentication layer at the FastAPI entry point.
*   **Approach:** An `AuthMiddleware` (or FastAPI Dependency) that supports three configurable modes via the `AUTH_MODE` environment variable.
    *   `NOAUTH`: Accepts all requests. Used exclusively for local development and testing.
    *   `API_KEY`: Requires a statically configured API Key passed via `Authorization: Bearer <token>` or `X-API-Key` headers. Suitable for CI/CD and simple internal deployments.
    *   `PROXY_HEADER`: Trusts a specific header (e.g., `X-Synarch-User`) set by an upstream identity-aware proxy (like Cloudflare Access or OAuth2 Proxy). This represents the production "hosted beta" setup.

## 2. Request Attribution (FR-42)
To avoid threading user IDs through every single function signature down to the database persistence layer, we will use context variables.
*   **Approach:**
    *   Define a `RequestContext` using Python's `contextvars` module.
    *   The `AuthMiddleware` extracts the user/actor identity from the authentication phase and sets it in the `RequestContext`.
    *   Downstream layers (like `PostgresEventRepository`, `PostgresApprovalRepository`) will automatically read the current actor from the `RequestContext` when persisting data (e.g., setting the `agent` field on events or `requested_by` on approvals).

## 3. Secrets Discipline & Redaction (FR-44)
We must ensure sensitive configuration values are never accidentally leaked in event streams or logs.
*   **Approach:**
    *   **Secret Registry:** Introduce a central `SecretRegistry` that stores active secret values.
    *   **Pydantic `SecretStr`:** Enforce that all agent tool configurations (e.g., GitHub tokens, external API keys) are loaded using Pydantic's `SecretStr`. We will patch or hook into the configuration loading process to automatically register the unwrapped values of these `SecretStr`s with the `SecretRegistry`.
    *   **Event Redaction Filter:** Implement a JSON serialization hook in `EventEnvelope.to_json_bytes()` (or a middleware immediately preceding NATS publication). This hook will scan the stringified payload and replace any exact matches of registered secrets with `***REDACTED***`.
    *   **Logging Filter:** Add a standard library logging filter that performs the same redaction on all log output.

## Security Considerations
*   **Performance:** String replacement on large JSON payloads can be slightly expensive. The redaction logic should compile the active secrets into an efficient Aho-Corasick automaton or a single optimized regex if the number of secrets grows.
*   **Spoofing:** When `PROXY_HEADER` mode is active, the application *must* reject requests not originating from the trusted proxy network, or rely on infrastructure-level firewalls to prevent header spoofing. (This will be documented as an operational requirement).
