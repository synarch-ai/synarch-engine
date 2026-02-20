# TypeScript Core Guidance (Concise)

## Default Stack
- Runtime: Bun (primary). Ensure compatibility with Node 20 LTS APIs.
- Frameworks: Fastify (default), NestJS, Express, or tRPC
- Validation: Zod at boundaries; generate OpenAPI where applicable
- Data: Prisma or TypeORM; use migrations for schema evolution
- Observability: OpenTelemetry tracing + metrics

## Correctness
- Strict tsconfig (noImplicitAny, strictNullChecks, exactOptionalPropertyTypes)
- Zod validation at every external boundary
- Versioned API contracts and event schemas

## Reliability
- Timeouts on all outbound calls (HTTP, DB, queues)
- Bounded retries with jitter and idempotency keys
- Circuit breakers for degraded dependencies

## Performance
- Avoid blocking I/O on the event loop
- Right-size pools and queues; apply backpressure
- Cache hot reads with TTL and stampede protection

## Testing
- Unit tests for core logic and invariants
- Integration tests with real DB/queue (Testcontainers)
- Contract tests for APIs and events
- Load tests for P95/P99 targets
