"""Tests for the leakage checker service."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.services.leakage import check_leakage, rewrite_to_safe_hint, FINAL_ANSWER_PATTERNS


LEAKY_RESPONSES = [
    "The answer is 42",
    "Therefore x = 7",
    "So x = 4",
    "Answer: 3.14",
    "x = 12",
    "The final answer is 99",
    "The solution is 5",
    "The result is 8",
]

SAFE_RESPONSES = [
    "Let's think about what we know",
    "What operation would help isolate x?",
    "Try applying the distributive property",
    "What happens when you subtract 5 from both sides?",
    "You're on the right track! Can you check your arithmetic?",
    "Think about the relationship between multiplication and division",
]


@pytest.mark.parametrize("response", LEAKY_RESPONSES)
def test_leakage_detected(response):
    assert check_leakage(response) is True, f"Should detect leakage in: {response}"


@pytest.mark.parametrize("response", SAFE_RESPONSES)
def test_no_false_positives(response):
    assert check_leakage(response) is False, f"False positive for: {response}"


def test_rewrite_clears_hint_level():
    result = rewrite_to_safe_hint({"hint_level_served": 4, "intent": "ask_for_answer"})
    assert result["telemetry"]["hint_level_served"] == 0
    assert result["telemetry"]["policy_violation_prevented"] is True


def test_rewrite_provides_student_message():
    result = rewrite_to_safe_hint()
    assert isinstance(result["student_message"], str)
    assert len(result["student_message"]) > 10


def test_rewrite_with_no_telemetry():
    result = rewrite_to_safe_hint()
    assert result["telemetry"]["policy_violation_prevented"] is True
