# Python Core Guidance (Concise)

## Default Stack
- Python: 3.11 or 3.12
- Framework: FastAPI (default). Django for monoliths with strong admin needs
- ASGI: Uvicorn + Gunicorn workers for production
- Data: SQLAlchemy or async SQLAlchemy; Alembic for migrations
- Messaging: Kafka or RabbitMQ; transactional outbox for reliability

## Performance and Reliability
- Use async for I/O bound code; avoid blocking calls in async handlers
- Set timeouts for DB, HTTP, and external APIs
- Use connection pools and limit concurrency
- Cache hot reads with TTL and stampede protection

## Observability
- OpenTelemetry for tracing and context propagation
- Structured JSON logging with request and trace ids
- Metrics: RED/USE plus business KPIs

## Security
- AuthN/OAuth2/JWT with strict authz checks
- Secrets via vault/KMS; never in code or logs
- Validate input; use allowlists for user-controlled parameters

## Testing
- Unit tests with pytest
- Integration tests with Testcontainers or docker-compose
- Contract tests for APIs and events
- Load tests with k6 or locust

## Tooling
- Type hints and mypy/pyright for core modules
- Ruff for linting and formatting
- Pre-commit for consistent CI gates
