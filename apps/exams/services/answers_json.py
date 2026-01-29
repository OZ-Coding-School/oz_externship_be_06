from __future__ import annotations

from typing import Any


def normalize_answers_json(raw: Any) -> list[dict[str, Any]]:
    if not raw:
        return []

    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]

    return []
