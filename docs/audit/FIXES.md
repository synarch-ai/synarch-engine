# synarch-engine fixes (branch fix/audit-2026-10)

Baseline: 18 tests pass (with temp Postgres). Final: 46 pass, 0 fail (`pytest tests` in backend/, temp Postgres 127.0.0.1:55434, since stopped and deleted).
Each new test was run against the pre-fix code (stash) and failed, then passed after.

| ID | Status | Commit | Test evidence | Remaining / owner decision |
|---|---|---|---|---|
| SYN-015 | fixed | 2217439 | tests/unit/test_syn015_auth.py: 401 without/with wrong key on missions, agents, metrics; X-API-Key and Bearer accepted; /health open; default host 127.0.0.1, reload off; non-loopback bind refused without key | Key is set with env `API_KEY`; non-loopback deployments must set it. start.sh now binds 127.0.0.1. Later commits moved the check outside idempotency, enforced loopback-only without a key, and added a server-side dashboard proxy (see PR #70). Remaining follow-ups are kept privately by the owner. |
| SYN-037 | fixed | 5ddb525 | test_syn037_parallel_branches.py: research+engineering mission failed with InvalidUpdateError before, completes now | none |
| SYN-041 | fixed (folds SYN-055) | 3a1a773 | test_syn041_janus_verdict.py (parse_verdict table; before: ImportError) | Prompt now asks for a `VERDICT:` line; unparseable output -> REVISE. Structured output still a future improvement. |
| SYN-038 | fixed (folds SYN-056) | ca8668e | test_syn038_revise_exhausted.py: exhausted REVISE routes to fail, mission FAILED, no synthesis call (before: COMPLETED) | Revision loop still only re-runs Zeus path (not Thoth). |
| SYN-004 | fixed (folds SYN-022) | 1664440 | test_syn004_souls.py: absolute souls_dir, loads from other cwd, missing soul raises, soul endpoint works from other cwd, unknown agent 404 | Missing soul now fails the mission loudly (intended). |
| SYN-005 | fixed (folds SYN-040) | 4be647b | test_syn005_lifecycle.py: cancel stops task with no bogus error_context; pause then resume completes; finishing task cannot overwrite cancelled | Pause/cancel stop the in-process task only; no cross-replica signalling. |
| SYN-039 | fixed | 82fd2cb | test_syn039_resume_and_lease.py: restart resumes from checkpoint (one planning call total); leased mission not run by second worker | Lease is a Redis SET NX EX with renewal (not Postgres advisory lock/SKIP LOCKED). Not exercised against a real Postgres checkpointer (MemorySaver in tests). |
| SYN-054 | fixed | 0e73469, ec0ad4c (compose mounts) | test_syn054_result_persistence.py: runtime persists result, state endpoint returns final_output/deliverables/messages/tasks, real-Postgres round trip | Requires new migration 003_mission_result.sql (compose now mounts 002 and 003; existing DBs must apply 003; reads degrade to empty if missing, write failure is logged). Stored in mission_payloads.result JSONB, not the tasks/deliverables tables. |
| SYN-007 | partial | via 0e73469 | state endpoint now returns real tasks/deliverables | HITL approval flow and the remaining repositories are not implemented: large design work, owner decision. |
| SYN-001 | not restored; recorded | none | n/a | Code removed by commit 26e6664 was inspected but not restored; restoring or formally dropping it is an owner decision (details kept privately). |

Notes
- Test helper FakeRedis (test_s02_runtime.py) gained set/get; in-memory repos gained `result` kwarg; test NoopMissionRuntime gained stop_mission.
- Existing test fakes key on system prompts; real souls now load and mention other agents, so new tests key on the user prompt.
- Cleanup: temp Postgres stopped and data dir removed; no servers left; backend/.venv exists in the worktree (gitignored).
