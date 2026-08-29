# Plan 005: Replace datetime.utcnow() with timezone-aware UTC

> **Executor instructions**: Follow this plan step by step. Run every verification command and confirm the expected result before moving to the next step.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: tech-debt
- **Planned at**: commit `8bb4058`, 2026-08-29

## Why this matters

Python 3.12+ deprecates `datetime.utcnow()`. The test suite emits 75 `DeprecationWarning`s. Future Python versions may remove the API.

## Current state

Usages in domain models and tests:

- `backend/domain/models/mission.py`
- `backend/domain/models/task.py`
- `backend/domain/models/deliverable.py`
- `backend/domain/models/approval.py`
- `backend/domain/models/memory.py`
- `backend/domain/models/agent_message.py`
- `backend/domain/events/envelope.py`
- `backend/tests/unit/test_s02_runtime.py`
- `backend/tests/integration/test_missions_api.py`

Pattern to replace:

```python
from datetime import datetime
datetime.utcnow()  # deprecated
```

Replacement:

```python
from datetime import datetime, timezone
datetime.now(timezone.utc)
```

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Find usages | `rg 'utcnow' backend/` | zero matches after fix |
| Tests | `python -m pytest -q` | 18 passed, 0 utcnow warnings |

## In scope

All files under `backend/` matching `utcnow`

## Out of scope

- Frontend date handling
- Database migration of stored timestamps

## Steps

1. `rg -l 'utcnow' backend/` — enumerate files.
2. Replace with `datetime.now(timezone.utc)`; add `timezone` import.
3. Consider a shared helper `backend/domain/time.py` with `def utc_now() -> datetime` if duplication exceeds 5 sites — optional, not required.
4. Run pytest with warnings as errors for DeprecationWarning: `python -m pytest -q -W error::DeprecationWarning` or confirm warning count drops to 0 for utcnow.

## Done criteria

- [ ] `rg 'utcnow' backend/` returns no matches
- [ ] `python -m pytest -q` — 18 passed
- [ ] No new utcnow DeprecationWarnings in test output

## STOP conditions

- Serialized JSON timestamps change format and break API contract tests — preserve `.isoformat()` behavior and report.
