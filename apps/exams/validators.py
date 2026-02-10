from typing import Any, Callable, Iterable

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


def parse_optional_positive_int(value: Any, error_message: ErrorMessages) -> int | None:
    """옵션 양의 정수 파라미터를 검증하고 없으면 None을 반환합니다."""
    if value is None or value == "":
        return None
    return parse_positive_int(value, error_message)


def parse_sort_order(
    *,
    sort: str | None,
    order: str | None,
    allowed_sort: set[str],
    allowed_order: set[str],
    default_sort: str,
    default_order: str,
    error_message: ErrorMessages,
) -> tuple[str, str]:
    """정렬 파라미터를 검증하고 기본값을 적용합니다."""
    sort_v = sort or default_sort
    order_v = order or default_order
    if sort_v not in allowed_sort or order_v not in allowed_order:
        raise_error(error_message)
    return sort_v, order_v


def normalize_optional_str(value: Any, *, max_length: int | None, error_message: ErrorMessages) -> str | None:
    """문자열 파라미터를 정규화하고 길이를 검증합니다."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise_error(error_message)
    normalized = value.strip()
    if not normalized:
        return None
    if max_length is not None and len(normalized) > max_length:
        raise_error(error_message)
    return normalized


def validate_time_range(
    open_at: Any,
    close_at: Any,
    *,
    error_message: ErrorMessages,
    exc_factory: Callable[[str], Exception] | None = None,
) -> None:
    """시간 범위를 검증합니다."""
    if open_at and close_at and open_at >= close_at:
        _raise_with(error_message, exc_factory)


def validate_duration_minutes(
    duration_time: Any,
    *,
    error_message: ErrorMessages,
    exc_factory: Callable[[str], Exception] | None = None,
) -> None:
    """시험 시간(분)이 양의 정수인지 검증합니다."""
    if not isinstance(duration_time, int) or duration_time <= 0:
        _raise_with(error_message, exc_factory)


def validate_duration_within_window(
    open_at: Any,
    close_at: Any,
    duration_time: Any,
    *,
    error_message: ErrorMessages,
    exc_factory: Callable[[str], Exception] | None = None,
) -> None:
    """시험 시간이 배포 기간을 넘지 않는지 검증합니다."""
    if not open_at or not close_at:
        return
    window_minutes = (close_at - open_at).total_seconds() / 60
    if not isinstance(duration_time, int) or duration_time > window_minutes:
        _raise_with(error_message, exc_factory)


def parse_choice(
    value: Any,
    *,
    allowed: Iterable[str],
    default: str,
    error_message: ErrorMessages,
    exc_factory: Callable[[str], Exception] | None = None,
    status_override: int | None = None,
) -> str:
    """허용된 선택지 내의 값인지 검증합니다."""
    resolved = (value or default) if isinstance(value, str) or value is None else default
    if resolved not in set(allowed):
        _raise_with(error_message, exc_factory, status_override=status_override)
    return resolved


def _raise_with(
    error_message: ErrorMessages,
    exc_factory: Callable[[str], Exception] | None,
    *,
    status_override: int | None = None,
) -> None:
    if exc_factory is None:
        raise_error(error_message, status_override=status_override)
    raise exc_factory(error_message.value)
