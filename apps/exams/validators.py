from typing import Any

from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error


def parse_positive_int(value: Any, error_message: ErrorMessages) -> int:
    """양의 정수 값인지 검증하고 실패 시 지정된 에러를 발생시킵니다."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise_error(error_message)
    if parsed <= 0:
        raise_error(error_message)
    return parsed
