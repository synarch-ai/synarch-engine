# synarch-engine review: branch fix/audit-2026-10

Reviewer: independent Opus review, 2026-10-08. Fix worktree, HEAD `ec0ad4c`, merge-base with origin/main `d12286c`. 9 commits. Nothing in the worktree was modified (git status clean before and after).

## Verdict: request-changes

The per-finding fixes are mostly real. Every new test fails on the parent commit and passes at HEAD. But 4 major problems need fixing before merge:

- 2 in the API-key work: the key check runs after the idempotency middleware, and there is a fail-open launch path.
- 1 in restart recovery: it is skipped when the process restarts within the lease TTL.
- 1 in migration 003: without it applied, every mission gets stuck.

Counts: blocker 0, major 4, minor 4, nit 8 (one nit omitted here).

Status after this review: M1-M4, m1-m4, n1 and n3 were fixed by later commits on PR #70, and n4 was addressed by the M2 commit. Remaining items are tracked privately by the owner.

## Per-commit verdicts

| Commit | ID | Verdict | Notes |
|---|---|---|---|
| 2217439 | SYN-015 | request-changes | Uses a timing-safe compare (`hmac.compare_digest`). But the check runs after IdempotencyMiddleware (M1), and the API is fail-open when `API_KEY` is unset and the server is started with the documented `uvicorn --host 0.0.0.0` (M2) |
| 5ddb525 | SYN-037 | approve | Root cause fixed. Test fails on the parent with `InvalidUpdateError`. Old checkpoints resume fine under the new reducers (probe) |
| 3a1a773 | SYN-041 | approve-with-nits | The anchored `VERDICT:` parse is good. The fallback still scans every line, so a bullet such as "- Pass rate..." still gives PASS (m2) |
| ca8668e | SYN-038 | approve | Dedicated synthesize node. Exhausted REVISE now fails. Dead locals left behind (n3) |
| 1664440 | SYN-004 | approve | Absolute souls_dir, a loud failure when a soul is missing, real 404s. Unused import in the test (n3) |
| 4be647b | SYN-005 | approve-with-nits | Cancel/pause stop the task, and `_finish` never overrides an external status. Route wiring is untested (m3). `stop_mission` swallows BaseException (n1) |
| 82fd2cb | SYN-039 | request-changes | Resume from checkpoint works. The lease blocks recovery after a crash (M3). Lease renew/release are not robust (m1) |
| 0e73469 | SYN-054 | request-changes | Result is persisted and exposed. Without 003 every `patch_payload` fails and missions get stuck in EXECUTING. The FIXES.md claim is false (M4) |
| ec0ad4c | SYN-054 | approve | Compose mounts 002/003. These only apply on a fresh volume (stated in FIXES.md) |

## Findings

### Major

**M1. The API-key check runs after IdempotencyMiddleware: 401s are cached, and cached 2xx responses are replayed without a key.**
- Where: `backend/api/app.py:26-28` (middleware) vs `:36-39` (router-level `Depends`). The middleware is in `backend/api/middleware/idempotency.py:65-128`.
- Evidence: a probe used the real middleware, a Postgres pool and `api_key="s3cret"`:
  - Unauthenticated POST `/api/v1/mission/start` with Idempotency-Key K returned 401.
  - The same request with a valid `X-API-Key` and the same K returned 401 again, with `X-Idempotent-Replay: true`. A legitimate retry after fixing the key is locked out for the 24h TTL.
  - Authenticated POST with K2 returned 201. The same body and K2 with no key returned 201 as a replay, including `mission_id`.
  - Unauthenticated callers also get a DB write (`idempotency_records` row) per POST.
- The auth tests miss this because they all use `enable_idempotency=False`.
- Suggested fix:
  - Do auth as an outermost ASGI middleware, before idempotency.
  - Or have IdempotencyMiddleware check auth first, or at least never store 401/403 responses.
  - Add a test with idempotency enabled.

**M2. Auth is fail-open when `API_KEY` is unset; the loopback-only claim holds only for `python main.py`.**
- Where: `backend/api/security.py:28` (no key means no-op); `backend/main.py:59-64` (`resolve_bind` only runs under `__main__`).
- `AGENTS.md:38` still documents `uvicorn main:app --host 0.0.0.0 --port 8000`. SETUP.md also uses the `uvicorn main:app` CLI.
- On that path there is no key, no bind check and no warning, so the API is fully exposed. FIXES.md says "with none set the API is open but loopback-only". That is not enforced on the documented launch path.
- Suggested fix, any one of:
  - When no key is set, reject requests whose `request.client.host` is not loopback.
  - Or require `API_KEY` unless an explicit `ALLOW_UNAUTHENTICATED=1` is set.
  - At minimum, log a loud startup warning.
- Also update AGENTS.md:38 and `.env.example`.

**M3. Restart recovery is skipped after a hard crash, and nothing retries.**
- Where: `backend/domain/orchestrator/runtime.py:208-215` and `:273-283`.
- A crashed process never runs its `finally`, so its lease survives for `mission_lease_seconds` (120s). A restart within that window (a container restart takes seconds) runs `resume_inflight_missions`, which logs "leased by another worker; skipping" and returns.
- Probe: kill the task mid-Zeus, keep the lease key, start a fresh runtime and call `resume_inflight_missions`. Result: status stays `executing`, 0 calls, no task scheduled. The mission stays stuck until another restart or a manual POST /resume after the TTL expires.
- The SYN-039 test misses this because it simulates the crash with `stop_mission`, and that path releases the lease in `finally`.
- Suggested fix:
  - Re-schedule skipped missions after the lease TTL, or run a periodic reconciler.
  - Or use a session-scoped Postgres advisory lock, which is released when the connection dies, as the finding suggested.
  - Add a hard-crash test.

**M4. Migration 003 is a hard dependency for every mission, not only for results.**
- Where: `backend/adapters/postgres/repositories.py:471`. `patch_payload` always lists the `result` column, even when `result` is None. The unguarded `patch_payload(plan=...)` call is at `backend/domain/orchestrator/runtime.py:344-347`.
- Probe on a DB with only 001 applied:
  - `get()` works (the `to_jsonb(mp)->'result'` fallback).
  - `patch_payload(plan=[...])` raises `UndefinedColumnError: column "result" ... does not exist`.
  - `run_mission` raises out of the `except` handler, because the error-context write fails too.
  - The mission stays `executing` with `error_context=None`, and it gets stuck again on every restart.
- FIXES.md says "reads degrade to empty if missing, write failure is logged". The logging part only covers the separate `result=` call; every other write fails.
- Existing compose volumes do not get 003 automatically (initdb runs only on a fresh volume).
- Suggested fix:
  - Build the INSERT/UPDATE column list dynamically, so `result` is only included when passed.
  - Or check for the column at startup and fail fast with a clear message.

### Minor

**m1. The Redis lease is not fail-safe.**
- Where: `runtime.py:200-222`.
- (a) `_renew_lease` dies on the first Redis error, and the mission keeps running unleased. Probe: a single `ConnectionError` on GET killed the renewer while the run continued. After the lease expired, a second runtime ran the same mission concurrently (9 LLM calls instead of 5).
- (b) Lease loss is never detected, and nothing stops the run.
- (c) Renew (GET then EXPIRE) and release (GET then DEL) are not atomic, so a worker can extend or delete another worker's lease.
- Suggested fix: compare-and-expire and compare-and-delete in a Lua script, catch errors and retry in the renewer, and cancel the mission task when the lease is lost.

**m2. The Janus fallback is not really anchored.**
- Where: `backend/domain/agents/janus.py:10`. `_LEADING_TOKEN` uses `re.M`, so it matches at the start of any line.
- Probe results:
  - `"Review summary:\n- Pass rate of the tests is only 40%..."` gives PASS.
  - `"Overall this needs work.\nFail-safe handling is missing"` gives FAIL.
- So when the model omits the VERDICT line, a silent PASS is still possible, which was the original defect class.
- Suggested fix: apply the fallback only to the first non-empty line, and require `:`/end-of-line after the token.

**m3. Test gaps.**
- `NoopMissionRuntime.stop_mission`/`launch_mission` (`tests/integration/test_missions_api.py:118-122`) record nothing, so no test checks that the cancel/pause/resume routes call the runtime.
- The SYN-005 pause/resume test runs with `require_durable_checkpointer=False`, so it covers restart-from-scratch, not resume. I checked resume separately in a probe with MemorySaver: one planning call, completes.
- Several "fails before" results are only ImportError/AttributeError: SYN-015, SYN-041, two of the three SYN-005 tests and two of the three SYN-054 tests.

**m4. Enum objects in checkpointed state.**
- `domain/agents/synarch.py:48,77` put `MissionPhase` enum objects into state.
- With checkpoint resume now in use, LangGraph 1.2.14 warns: "Deserializing unregistered type ... MissionPhase ... will be blocked in a future version". Under `LANGGRAPH_STRICT_MSGPACK`, or after a LangGraph upgrade, resume would break.
- The write predates this branch, but SYN-039 now depends on reading it back.
- Fix: write `.value`.

### Nits

1. `runtime.py:229-233`: `stop_mission` catches `BaseException`. That also swallows the caller's own `CancelledError`, for example on client disconnect or shutdown.
2. `runtime.py:396-397`: the budget counter is never cleared on cancel (kept for pause, which is fine). The key lingers until its 24h TTL.
3. `domain/agents/synarch.py:12-14`: dead locals after the branch removal (ruff F841 `phase` is new). `tests/unit/test_syn004_souls.py:2`: unused `os`.
4. `AGENTS.md:38` still says `--host 0.0.0.0` and "python main.py (adds --reload)". `.env.example` does not mention `API_KEY`.
5. `config.py` `host`/`port`/`reload` read the generic env vars `HOST`/`PORT`/`RELOAD` (no prefix). A stray `HOST` breaks `python main.py`, but it fails closed.
6. `test_postgres_roundtrip_result` applies DDL (003) to whatever `TEST_DATABASE_URL` points at.
7. `to_jsonb(mp)` in `get()` serializes the whole payload row on every read. Fine now; switch to a direct column once 003 is mandatory.

### Checked and OK

- `hmac.compare_digest` on bytes (leaks length only). Bearer parsing is case-insensitive. OPTIONS bypass is correct. `/health` stays open. Agent names are allow-listed, so the soul route has no path traversal.
- Migration 003 is `ADD COLUMN IF NOT EXISTS result JSONB` with no default: metadata-only, idempotent, no data loss. Applied by `db-bootstrap.sh` (glob) and compose (fresh volumes).
- SYN-037: `last_value` on `current_agent`/`phase` is the right minimal fix. Only `current_agent` was written by both branches. A checkpoint written under the old schema resumes correctly under the new one (probe, LangGraph 1.2.14).
- SYN-039:
  - `ainvoke(None)` on a finished thread returns the final state with 0 extra LLM calls (probe).
  - Pause then resume with a durable saver resumes without re-planning (probe).
  - Pause releases the lease.
- SYN-005: `_finish` and the `MISSION_INVALID_TRANSITION` catch prevent "completed over cancelled". The `_cleanup` identity check stops an old task's callback from evicting a relaunched task.
- No secrets, no dependency or lockfile changes, no web changes.

## Check results

Postgres for the tests:
- I used Homebrew PostgreSQL 18 with pgvector 0.8.7, run TCP-only on 127.0.0.1:55435 with `synarch` role/db and 001 applied.
- This is a deviation from SETUP.md, which uses the `pgvector/pgvector:pg16` docker image. That image was not cached locally, and this avoided a pull.
- The server was stopped and its data dir deleted afterwards.
- The throwaway base worktree was removed and pruned. No listeners are left.

| Check | Base d12286c | HEAD ec0ad4c |
|---|---|---|
| pytest with DB | 18 passed | 46 passed, 0 skipped |
| pytest without DB | 16 passed, 2 failed (env) per SETUP | 43 passed, 2 failed (same postgres integration tests, env), 1 skipped |
| Per-commit new tests on parent code | n/a | all fail (8/8 commits with tests); all pass at HEAD |
| `compileall` backend | ok | ok |
| `ruff --isolated --select F` (repo has no lint config) | 29 | 31 (+F841 `synarch.py:14 phase`, +F401 `test_syn004_souls.py:2 os`) |
| Web (tsc / next build) | not run | not run: no `apps/` changes on the branch, node_modules not installed |

## FIXES.md claims not confirmed or false

- **False:** SYN-054 "reads degrade to empty if missing, write failure is logged". Reads degrade, but every write fails and missions get stuck (M4).
- **Overstated:** SYN-015 "with none set the API is open but loopback-only". This holds only under `python main.py` (M2).
- **Partial:** SYN-039 "restart resumes from checkpoint". True for a clean stop. After a hard crash, a restart within 120s skips recovery (M3).
- **Not verifiable here:** behaviour with the real Postgres checkpointer (all tests use MemorySaver or FakeCheckpointer; FIXES.md itself says so).
- **Not verifiable here:** cross-replica pause/cancel (acknowledged as not implemented).
- **Confirmed:**
  - 46 pass.
  - Each new test fails before the fix (several via ImportError/AttributeError, m3).
  - SYN-001 and SYN-007 are recorded honestly as not restored / partial.
