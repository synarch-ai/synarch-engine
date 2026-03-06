# Design Document: S15 - Regression Eval Suite & Quality Dashboards

**Date:** 2026-02-23
**Focus:** FR-48 (Regression Eval Suite in CI) and FR-49 (Multi-dimensional quality/latency/cost/safety dashboards).
**Aesthetic Theme:** The Floating Glass Observatory (Opaque Nexus)

## 1. Regression Eval Suite (FR-48)

**Architecture:** Dual-Tier Pipeline
We will implement a two-tiered testing strategy to ensure LLM evaluation reliability and agent prompt regression safety.

*   **Tier 1: Static CI Evaluation**
    *   **Goal:** Fast, deterministic testing of the `EvalRunner` parsing and thresholds.
    *   **Component:** `backend/tests/integration/test_s15_regression.py`
    *   **Mechanism:** Uses mocked LLM outputs against a static golden dataset (`tests/datasets/golden_evals.json`) to verify the judge accurately scores deliverables.
*   **Tier 2: Live Mission Evaluation CLI**
    *   **Goal:** End-to-end regression testing of agent behavior and prompt efficacy against real LLM APIs.
    *   **Component:** `scripts/run_evals.py`
    *   **Mechanism:** CLI tool that loads goals from the golden dataset, spawns real LangGraph missions, waits for completion, and uses the live `EvalRunner` to grade the *newly* produced deliverables.

## 2. Data Architecture (FR-49)

**Architecture:** Asynchronously Refreshed Materialized Views
To scale massive mission throughput without degrading core OLTP performance, we decouple analytics from orchestration.

*   **View Definition:** `daily_mission_metrics` materialized view aggregating by `metrics_date` and `authority_mode`. Includes sums of costs, tokens, and counts of missions.
*   **Refresh Strategy:** Asynchronous Background Worker. A periodic task (or cron/NATS worker) executes `REFRESH MATERIALIZED VIEW CONCURRENTLY` to provide eventual consistency (e.g., 5 min delay) with zero DB locking contention.
*   **API Layer:** `GET /api/v1/metrics/daily` endpoint fetches pre-aggregated rollup data to serve the frontend.

## 3. Frontend Dashboard Interface

**Aesthetic:** The Floating Glass Observatory (Opaque Nexus)
A high-end, elegant Enterprise dashboard avoiding generic AI aesthetics.

*   **Visual Tone:** Deep, dark, desaturated gradient mesh backgrounds with heavy cinematic grain.
*   **Components:** Metric cards use layered Glassmorphism (`backdrop-filter: blur(24px)`) with subtle soft-clay extruded inner shadows to simulate physicality.
*   **Typography:** `Outfit` for sleek headers and structural text. `JetBrains Mono` for precise, raw data points (costs, token counts).
*   **Motion:** Staggered, delayed CSS-only entrance animations where glass panels "fade and float" into position on page load.
*   **Charts:** Built with Recharts or similar, utilizing glowing neon strokes and translucent gradient fills over pure black inner canvases.
