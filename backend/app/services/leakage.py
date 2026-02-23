import re
import copy
from typing import Tuple


FINAL_ANSWER_PATTERNS = [
    r"(?i)\bthe answer is\b",
    r"(?i)\btherefore[,\s]+[a-z]?\s*=\s*[\d\.]+",
    r"(?i)\bso[,\s]+[a-z]?\s*=\s*[\d\.]+",
    r"(?i)^Answer:\s*.+",
    r"(?i)\bx\s*=\s*[\d\.]+\b",
    r"(?i)\bfinal answer\b",
    r"(?i)\bthe solution is\b",
    r"(?i)\bresult is\s+[\d\.]+",
    r"(?i)=\s*[\d\.]+\s*$",
]


def check_leakage(response_text: str) -> bool:
    """Returns True if the response likely contains a final answer."""
    for pattern in FINAL_ANSWER_PATTERNS:
        if re.search(pattern, response_text, re.MULTILINE):
            return True
    return False


SAFE_REDIRECT = {
    "student_message": (
        "I want to help you reach the answer yourself! Let's think through this step by step. "
        "What do you already know about this problem? Try writing out what you think the first step might be."
    ),
    "check_question": "What information do you have to start with?",
    "next_action": "hint",
    "telemetry": {
        "intent": "ask_for_answer",
        "skill_tags": [],
        "stuck_step": 1,
        "hint_level_served": 0,
        "misconception_code": None,
        "policy_violation_prevented": True,
    },
}


def rewrite_to_safe_hint(original_telemetry: dict | None = None) -> dict:
    """Return a safe hint response when leakage is detected."""
    safe = copy.deepcopy(SAFE_REDIRECT)
    if original_telemetry:
        telemetry = safe["telemetry"].copy()
        telemetry["intent"] = original_telemetry.get("intent", "ask_for_answer")
        telemetry["skill_tags"] = original_telemetry.get("skill_tags", [])
        telemetry["stuck_step"] = original_telemetry.get("stuck_step", 1)
        telemetry["hint_level_served"] = 0
        telemetry["policy_violation_prevented"] = True
        safe["telemetry"] = telemetry
    return safe
