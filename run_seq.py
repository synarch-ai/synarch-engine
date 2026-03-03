import json

def seq(thought, thought_num, total_thoughts, next_needed, **kwargs):
    payload = {
        "thought": thought,
        "thoughtNumber": thought_num,
        "totalThoughts": total_thoughts,
        "nextThoughtNeeded": next_needed,
    }
    payload.update(kwargs)
    print(json.dumps(payload, indent=2))

seq("Approach A (Custom Telemetry Node/Callback) aligns better with the Event System we already built (EventEnvelope has a `telemetry` field with `cost_usd`, `latency_ms`, `tokens`). We should wire this up.", 7, 20, True, isRevision=True, revisesThought=5)
seq("For the Eval baseline, we can implement an `eval` Python package within `backend/domain/` or `backend/tests/evals` that runs LLM-as-judge against completed missions or specific tasks. This satisfies FR-45 and FR-46.", 8, 20, True)
seq("S14 involves: \n1. Add a LangChain CallbackHandler to intercept LLM calls, calculate cost/tokens, and emit an event to the EventBus.\n2. Create an initial `eval_runner.py` that can evaluate a given mission's deliverables using an LLM-as-judge prompt.\n3. Verify cost and token telemetry works in the local flow.", 9, 20, False)
