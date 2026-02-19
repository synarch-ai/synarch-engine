# Synarch Adoption Enforcement Playbook

**Developer:** PraxLannister  
*Operational Governance | 2026-02-19 | Status: ACTIVE*

---

## Purpose

Turn ADR-004 from a policy document into mandatory implementation behavior.

This playbook defines how each architecture/runtime/UI change is reviewed, evidenced, and accepted.

---

## Scope

This applies to every PR that changes any of the following:

- `backend/src/orchestrator/*`
- `backend/src/agents/*`
- `backend/src/api/*`
- `backend/src/nervous_system/*`
- `apps/web/app/*`
- `apps/web/components/*`
- architecture docs under `docs/02-architecture/*`

---

## Required PR Artifacts

Every in-scope PR must include all of these:

1. **Contract mapping**
   - Which ADR-004 workstream(s) are impacted (`W1` to `W5`)
   - Which reference repo pattern(s) are used

2. **Matrix update**
   - Update `docs/02-architecture/reference-adoption-matrix.md`
   - Move status forward only when acceptance signal is proven

3. **Progress update**
   - Update `memory-bank/progress.md` milestone checkboxes

4. **Evidence bundle**
   - Tests or contract checks used
   - Manual verification notes (if required)
   - File/path references for implementation proof

---

## Review Gates

### Gate A: Architecture Fit

- Does the change align with ADR-004 and ADR-003?
- Is there any hidden runtime migration risk?

### Gate B: Runtime Safety

- Is idempotency behavior clear for side effects?
- Are pause/resume and recovery semantics explicit?

### Gate C: Operator UX

- Is mission phase visible in UI?
- Are guardrails and approvals operator-visible and actionable?
- Is the V3 design system actually used (not approximated)?

PR cannot be merged until all three gates are satisfied.

---

## Definition of Adopted (Matrix Status)

A matrix row can be marked `adopted` only if all are true:

1. Pattern is implemented in Synarch runtime/UI.
2. Acceptance signal in the matrix is demonstrably met.
3. Evidence is referenced in PR notes.
4. `memory-bank/progress.md` reflects completion.

If any of the above is missing, row must stay `in_progress`.

---

## Non-Compliance Handling

If an in-scope PR misses required artifacts:

1. Mark PR as `changes requested`.
2. Add missing matrix/progress/evidence updates.
3. Re-run review only after artifacts are present.

---

## Cadence

- Enforce on every in-scope PR.
- Reconcile matrix vs progress once per active sprint.
- Reconfirm top priorities before each milestone planning cycle.
