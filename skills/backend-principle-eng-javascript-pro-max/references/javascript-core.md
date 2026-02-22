# JavaScript Core Guidance (Concise)

## Default Stack
- Runtime: Bun (primary). Ensure compatibility with Node 20 LTS APIs.
- Frameworks: Fastify (default), NestJS, Express, or tRPC
- Validation: Zod at boundaries; generate OpenAPI where applicable
- Data: Prisma or TypeORM; use migrations for schema evolution
- Observability: OpenTelemetry tracing + metrics

## Correctness
- Validate inputs at boundaries (Zod or JSON schema)
- Version API contracts and events
- Enforce invariants in service and database

## Reliability
- Timeouts on all outbound calls (HTTP, DB, queues)
- Bounded retries with jitter and idempotency keys
- Circuit breakers for degraded dependencies

## Performance
- Avoid blocking I/O on the event loop
- Right-size pools and queues; apply backpressure
- Cache hot reads with TTL and stampede protection

## Testing and Linting
- Tests: Jest or Vitest; integration tests with Testcontainers
- Lint: ESLint with strict rules; Prettier for formatting
- Type safety: use JSDoc for public APIs if TypeScript is not used
