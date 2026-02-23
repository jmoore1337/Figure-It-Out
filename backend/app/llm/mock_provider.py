from typing import List, Dict
from app.llm.provider import LLMProvider


MOCK_HINTS = [
    "Let's start by thinking about what information we have. What do you know so far about this problem?",
    "Good thinking! Now, what operation or concept do you think might apply here? Try to identify the key relationship.",
    "You're making progress! Let's break it down into a smaller step. What would happen if you tried applying that concept to just the first part?",
    "Nice work breaking it down! Now think about what you'd do next. What does the result of that step tell you?",
    "Almost there! Can you write out what you think the next step would be? Give it a try and I'll help you check it.",
    "You've worked through this really well! Write out your full solution attempt and let's verify each step together.",
]


class MockProvider(LLMProvider):
    async def generate(self, messages: List[Dict[str, str]]) -> str:
        # Count assistant messages to determine hint level
        assistant_count = sum(1 for m in messages if m.get("role") == "assistant")
        hint_index = min(assistant_count, len(MOCK_HINTS) - 1)

        last_user = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"), ""
        )

        if "answer" in last_user.lower() or "tell me" in last_user.lower():
            return (
                '{"student_message": "I can\'t give you the final answer directly, but I can help you figure it out! '
                'Let\'s work through it step by step.", '
                '"check_question": "What do you already know about this problem?", '
                '"next_action": "hint", '
                '"telemetry": {"intent": "ask_for_answer", "skill_tags": [], "stuck_step": 1, '
                '"hint_level_served": 0, "misconception_code": null, "policy_violation_prevented": true}}'
            )

        hint = MOCK_HINTS[hint_index]
        return (
            f'{{"student_message": "{hint}", '
            f'"check_question": "Does that make sense so far?", '
            f'"next_action": "hint", '
            f'"telemetry": {{"intent": "ask_for_hint", "skill_tags": [], "stuck_step": 1, '
            f'"hint_level_served": {hint_index}, "misconception_code": null, "policy_violation_prevented": false}}}}'
        )
