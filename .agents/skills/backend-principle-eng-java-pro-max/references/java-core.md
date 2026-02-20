# Java Core Guidance (Concise)

## Default Stack
- JDK: 21 LTS (prefer latest patch)
- Framework: Spring Boot 3.x (default). Alternatives: Micronaut or Quarkus for low-latency or fast startup
- Build: Gradle (kts) or Maven with BOMs and reproducible builds
- HTTP: Prefer Netty for high concurrency; avoid blocking in reactive stacks
- Serialization: Jackson with explicit schemas; avoid reflection in hot paths
- Validation: Jakarta Bean Validation at boundaries
- Persistence: JPA/Hibernate for OLTP; jOOQ for query-heavy paths
- Messaging: Kafka with idempotent producers; transactional outbox for reliability

## Performance and Reliability
- Set timeouts for every outbound call (connect, read, write)
- Use HikariCP with sensible min/max; avoid pool starvation
- Separate CPU and I/O pools; isolate heavy dependencies with bulkheads
- Prefer bounded queues; apply backpressure instead of unbounded buffering
- JVM: Use G1 or ZGC; let the JVM manage GC unless profiling shows issues

## Resilience Patterns
- Resilience4j for timeouts, retries, circuit breakers, bulkheads, rate limits
- Retries only for idempotent operations; add jitter and caps
- Graceful shutdown with drain period and in-flight request completion

## Observability
- OpenTelemetry for tracing and context propagation
- Micrometer for metrics; emit RED and USE metrics plus business KPIs
- Structured JSON logging with request id, trace id, and user/account id (redacted)

## Security
- OAuth2/JWT with strict authz checks in every service
- Secrets via vault/KMS; never commit or log secrets
- Encrypt data in transit; consider at-rest encryption for sensitive stores
- Input validation and output encoding to prevent injection

## Testing
- Unit tests for core logic and invariants
- Integration tests with Testcontainers for DB and Kafka
- Contract tests for APIs and events
- Load tests with Gatling or k6; measure P95/P99
