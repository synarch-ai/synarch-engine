# Implementation Plan: S13 - Build/lint/type + critical path CI gates (Issue #14)

## Objective
Implement mandatory CI/CD gates to enforce build quality, code linting, and type checking for both the frontend and backend, fulfilling FR-81 and FR-82.

## Context
As part of Phase 0-1 Runtime Closure, the system must enforce quality gates to prevent failing merges and broken builds. This ensures that the newly established frontend (S12) and backend (S01-S11) patterns remain stable.

## Components to Implement

1. **Backend CI Pipeline (GitHub Actions)**
   - Type Checking: `mypy` or `pyright` for `backend/`
   - Linting/Formatting: `ruff` check and format
   - Testing: `pytest` for `backend/tests/` (Unit and Integration)
   - FR-81 Compliance: Block PRs if backend tests fail.

2. **Frontend CI Pipeline (GitHub Actions)**
   - Linting: `npm run lint` (`eslint`)
   - Type Checking: `tsc --noEmit`
   - Build Gate: `npm run build`
   - FR-82 Compliance: Block PRs if Next.js build or types fail.

3. **Pre-commit Hooks (Optional but recommended)**
   - Provide `.pre-commit-config.yaml` to run local validations before pushing.

## Plan
1. Set up backend configuration files (`ruff.toml`, `pyproject.toml` updates if necessary).
2. Set up GitHub Actions workflow (`.github/workflows/ci.yml`) defining jobs for backend and frontend.
3. Validate locally by running the commands that the CI will run.
4. Verify tests pass (or fix broken ones).
5. Add/Update docs as required.
