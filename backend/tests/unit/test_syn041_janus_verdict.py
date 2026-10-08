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
])
def test_parse_verdict(text, expected):
    assert parse_verdict(text) == expected
