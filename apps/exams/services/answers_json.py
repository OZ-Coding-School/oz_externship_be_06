from __future__ import annotations

from typing import Any


def normalize_answers_json(raw: Any) -> list[dict[str, Any]]:
    if not raw:
        return []

    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]

    if isinstance(raw, dict):
        if isinstance(raw.get("answers"), list):
            return [item for item in raw["answers"] if isinstance(item, dict)]

        normalized: list[dict[str, Any]] = []
        for key, value in raw.items():
            try:
                question_id = int(key)
            except (TypeError, ValueError):
                continue
            normalized.append({"question_id": question_id, "submitted_answer": value})
        return normalized

    return []
