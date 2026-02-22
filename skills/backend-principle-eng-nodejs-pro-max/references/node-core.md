# Node.js Runtime Guidance (Concise)

## Runtime
- Primary: Bun (preferred). Ensure Node 20 LTS API compatibility.
- Avoid nonstandard APIs unless gated by runtime checks.

## Event Loop and Concurrency
- Avoid blocking sync work on the main thread
- Use worker threads for CPU-bound tasks
- Apply backpressure for streams and queues
- Set explicit limits on concurrency and queue depth

## Memory and Stability
- Watch heap growth and GC pauses
- Avoid unbounded caches or in-memory queues
- Use heap snapshots and profiling for leak detection

## Networking and I/O
- Set timeouts on all outbound requests
- Use keep-alive for HTTP clients
- Prefer streaming for large payloads

## Observability
- OpenTelemetry for tracing and metrics
- Monitor event loop lag, heap usage, and response latency

## Testing
- Unit tests for core logic and invariants
- Integration tests with real dependencies
- Load tests for P95/P99 targets
