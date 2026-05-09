"""Grounded station explanation prompts."""

from __future__ import annotations

import json
from typing import Any

MAX_HISTORY_MESSAGES = 6


def build_station_explanation_messages(
    *,
    station: dict[str, object],
    question: str | None = None,
    history: list[dict[str, object]] | None = None,
) -> list[dict[str, str]]:
    """Build a compact, fact-grounded prompt for explaining one station."""
    recent_history = _recent_history(history or [])
    station_payload = json.dumps(station, sort_keys=True)
    user_question = question or "Explain what happened at this station."

    messages = [
        {
            "role": "system",
            "content": (
                "You explain TokenKaki inference railway station facts to a hackathon user. "
                "Use only the provided station facts and reference metrics. "
                "Clearly distinguish live gateway-observed facts from benchmark reference metrics. "
                "If a metric is missing or inferred, say so plainly. Keep the answer under 90 words."
            ),
        }
    ]
    messages.extend(recent_history)
    messages.append(
        {
            "role": "user",
            "content": (
                f"Question: {user_question}\n\n"
                "Station facts JSON follows. Treat it as the source of truth:\n"
                f"{station_payload}"
            ),
        }
    )
    return messages


def extract_chat_text(content: bytes) -> str | None:
    """Extract assistant text from an OpenAI-compatible non-streaming response."""
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first = choices[0]
    if not isinstance(first, dict):
        return None
    message = first.get("message")
    if not isinstance(message, dict):
        return None
    content_value = message.get("content")
    if isinstance(content_value, str):
        return content_value
    return None


def _recent_history(history: list[dict[str, object]]) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for item in history[-MAX_HISTORY_MESSAGES:]:
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and isinstance(content, str) and content:
            messages.append({"role": role, "content": content})
    return messages
