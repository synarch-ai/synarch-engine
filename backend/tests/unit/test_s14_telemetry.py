import pytest
from domain.orchestrator.telemetry import TelemetryCallbackHandler

def test_telemetry_handler_records_and_accumulates():
    """Verify TelemetryCallbackHandler properly counts and groups latency and token usage."""
    handler = TelemetryCallbackHandler()

    # Assert initial zero state
    metrics = handler.get_and_reset_metrics()
    assert metrics["total_tokens"] == 0
    assert metrics["prompt_tokens"] == 0
    assert metrics["completion_tokens"] == 0
    assert metrics["total_cost_usd"] == 0.0
    assert metrics["total_latency_ms"] == 0.0

    # Record some calls
    handler.record_llm_call(
        model_name="gpt-4",
        prompt_tokens=100,
        completion_tokens=50,
        cost_usd=0.005,
        latency_ms=1200.0,
    )

    handler.record_llm_call(
        model_name="gpt-4",
        prompt_tokens=200,
        completion_tokens=150,
        cost_usd=0.015,
        latency_ms=3000.0,
    )

    # Retrieve & Check
    metrics = handler.get_and_reset_metrics()
    assert metrics["prompt_tokens"] == 300
    assert metrics["completion_tokens"] == 200
    assert metrics["total_tokens"] == 500
    assert metrics["total_cost_usd"] == 0.02
    assert metrics["total_latency_ms"] == 4200.0

    # Ensure it reset properly
    assert handler.total_tokens == 0
    assert handler.total_cost_usd == 0.0
