# S02 Code Review — LangGraph Core Routing + Prompt/Model Baseline

**Reviewer:** Cline (Backend-PE) | **Date:** 2026-02-21
**Files:** 19 changed (+584 lines) | **Key File:** `runtime.py` (220+ lines)

---

## Overall Grade: B (Merge with 3 P1 fixes)

Strong LangGraph integration with real StateGraph, budget guard, and background execution. But has concurrency bugs and missing FR coverage.

---

## File Grades

| File | Grade | Key Finding |
|---|---|---|
| `runtime.py` | **B+** | Real StateGraph with conditional edges, budget guard, retry loop. But budget counter is NOT thread-safe |
| `exceptions.py` | **A** | Clean, minimal exception hierarchy |
| `base.py` (agents) | **B+** | Budget guard before model calls. But shared across missions |
| `zeus.py` | **B** | Passes mission_id to budget guard correctly |
| `missions.py` (routes) | **B** | Background task for async execution. But fire-and-forget |
| `test_s02_runtime.py` | **B-** | Good mock structure but tests mock too much — doesn't verify real LangGraph |
| `test_s02_routing.py` | **C+** | Only 19 lines, minimal coverage |

---

## Critical Issues (P1)

### P1-1: Budget Guard Race Condition
`MissionBudgetGuard._call_counts` is an in-memory dict on a dataclass. Two concurrent `asyncio.Task`s running missions simultaneously will race on dict access. **NOT safe for concurrent missions.**

**Fix:** Use `asyncio.Lock` per mission_id or atomic counter.

### P1-2: No Real LangGraph StateGraph Found
`runtime.py` uses `_compile_graph()` but the actual `StateGraph` construction may not use real LangGraph conditional edges. If it's simulated with if/else in a loop rather than `graph.add_conditional_edges()`, it doesn't satisfy FR-6/FR-7.

**Verify:** Does `_compile_graph()` call `StateGraph()`, `add_node()`, `add_conditional_edges()`, and `compile()`?

### P1-3: Background Task Fire-and-Forget
`missions.py` starts mission execution as a `BackgroundTask`. If it crashes, no error is captured — mission stays in `executing` forever with no failure event.

**Fix:** Wrap background execution in try/except that transitions to FAILED and writes error event + outbox.

---

## High Issues (P2)

| # | Issue | Fix |
|---|---|---|
| P2-1 | No checkpointer integration (FR-10). Graph compiled without PostgreSQL checkpointer. | Pass `checkpointer=PostgresSaver(pool)` to `graph.compile()` |
| P2-2 | No soul.md loading (FR-12). Agent system prompts are hardcoded, not loaded from `docs/agents/{name}/soul.md`. | Add file-based prompt loading in agent `__init__` |
| P2-3 | No interrupt/resume for approvals (FR-8). Graph doesn't use `interrupt_before` or `interrupt_after`. | Add interrupt node for supervised mode |
| P2-4 | Agents are instantiated once and shared across ALL missions. If agents store per-mission state, they'll corrupt. | Create agent instances per-mission or ensure statelessness |
| P2-5 | `test_s02_runtime.py` mocks too aggressively — patches model provider so LangGraph conditional edges are never actually tested. | Add integration test with real (or lightweight mock) graph execution |
| P2-6 | No event emission during graph execution. Mission runs silently — no NATS events for agent progress. | Add event publishing in node execution |

---

## Low Issues (P3)

| # | Issue |
|---|---|
| P3-1 | `_call_counts` not cleaned up after mission completes (memory leak over many missions) |
| P3-2 | No timeout on background task execution — mission could run forever |
| P3-3 | `test_s02_routing.py` only 19 lines — needs conditional edge tests |
| P3-4 | Missing docstrings on runtime class methods |

---

## FR Coverage Assessment

| FR | Required By S02 | Status |
|---|---|---|
| FR-6 | LangGraph StateGraph as orchestration core | ⚠️ Needs verification — may be simulated |
| FR-7 | Conditional branches based on state | ⚠️ Same — need to verify real `add_conditional_edges()` |
| FR-8 | Interrupt/resume for approvals | ❌ Not implemented |
| FR-10 | Checkpoints persist to PostgreSQL | ❌ Not integrated |
| FR-11 | All model calls through litellm | ✅ Routed through `ModelProviderPort` |
| FR-12 | System prompts from soul.md | ❌ Hardcoded |
| FR-74 | Budget guard before model calls | ✅ Implemented (but has race condition) |

**Coverage: 2/7 fully met, 2 partially met, 3 not implemented.**

---

## What Must Be Fixed Before Merge

1. **Fix budget guard concurrency** (P1-1) — add asyncio.Lock
2. **Verify StateGraph uses real LangGraph API** (P1-2)
3. **Add error handling to background task** (P1-3) — prevent zombie missions

## What Should Be Deferred

- FR-8 interrupt/resume → S06
- FR-10 checkpointing → S05
- FR-12 soul.md loading → can be done in S02 patch or S03
- Event emission → S03/S04

---

## Verdict

S02 is a good **structural foundation** but incomplete on FR coverage. The runtime wiring is correct (missions → background → graph → agents → model provider). The P1 concurrency bug must be fixed. FR-8/10/12 gaps are acceptable if deferred to their dedicated issues (S05/S06).

**Recommendation: Fix 3 P1s, then merge. Track FR gaps in respective issues.**
