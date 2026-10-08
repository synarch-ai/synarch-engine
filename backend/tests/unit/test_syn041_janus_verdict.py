"""SYN-041 / SYN-055: Janus verdict must be parsed from an anchored verdict, not substrings."""
import pytest

from domain.agents.janus import parse_verdict


@pytest.mark.parametrize("text,expected", [
    ("PASS: no failures found, nothing to revise", "PASS"),
    ("VERDICT: PASS\nThe code has no failures; I would not REVISE anything.", "PASS"),
    ("**Verdict:** REVISE\nOne test would FAIL.", "REVISE"),
    ("Verdict: FAIL\nunsalvageable", "FAIL"),
    ("FAIL: does not meet criteria", "FAIL"),
    ("Looks great overall, ship it.", "REVISE"),
    ("", "REVISE"),
    ("Failure modes were considered; passing grade.", "REVISE"),
    # review m2: the fallback must not match a word at the start of any later line
    ("Review summary:\n- Pass rate of the tests is only 40%", "REVISE"),
    ("Overall this needs work.\nFail-safe handling is missing", "REVISE"),
    ("Pass rate is 40%", "REVISE"),
    ("PASS", "PASS"),
    ("**FAIL**\nbroken", "FAIL"),
    ("REVISE - add tests", "REVISE"),
    ("\n\nPASS.\nAll good.", "PASS"),
])
def test_parse_verdict(text, expected):
    assert parse_verdict(text) == expected
