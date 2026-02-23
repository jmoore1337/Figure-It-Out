"""Tests for policy enforcement in the tutor service."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_parse_llm_response_valid_json():
    from app.routers.tutor import parse_llm_response
    raw = '{"student_message": "Try again", "check_question": "What do you know?", "next_action": "hint", "telemetry": {"intent": "ask_for_hint", "skill_tags": [], "stuck_step": 1, "hint_level_served": 0, "misconception_code": null, "policy_violation_prevented": false}}'
    result = parse_llm_response(raw)
    assert result["student_message"] == "Try again"
    assert result["telemetry"]["intent"] == "ask_for_hint"


def test_parse_llm_response_invalid_json():
    from app.routers.tutor import parse_llm_response
    raw = "This is a plain text response"
    result = parse_llm_response(raw)
    assert result["student_message"] == raw
    assert result["telemetry"]["intent"] == "other"


def test_parse_llm_response_strips_markdown():
    from app.routers.tutor import parse_llm_response
    raw = '```json\n{"student_message": "ok", "check_question": "?", "next_action": "hint", "telemetry": {"intent": "other", "skill_tags": [], "stuck_step": 1, "hint_level_served": 0, "misconception_code": null, "policy_violation_prevented": false}}\n```'
    result = parse_llm_response(raw)
    assert result["student_message"] == "ok"


def test_policy_no_answer_mode():
    """Test that NO_ANSWER mode triggers leakage check."""
    from app.services.leakage import check_leakage, rewrite_to_safe_hint

    # A response with a final answer should be flagged
    leaky_response = "Therefore x = 4"
    assert check_leakage(leaky_response) is True

    # A safe hint should not be flagged
    safe_response = "Let's think about what operation would isolate x"
    assert check_leakage(safe_response) is False


def test_rewrite_to_safe_hint_preserves_intent():
    from app.services.leakage import rewrite_to_safe_hint

    original = {"intent": "ask_for_answer", "skill_tags": ["algebra"], "stuck_step": 2}
    result = rewrite_to_safe_hint(original)

    assert result["telemetry"]["policy_violation_prevented"] is True
    assert result["telemetry"]["intent"] == "ask_for_answer"
    assert result["telemetry"]["hint_level_served"] == 0
    assert "answer" not in result["student_message"].lower() or "help" in result["student_message"].lower()
