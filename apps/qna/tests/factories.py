from __future__ import annotations

from itertools import count
from typing import Any

from apps.users.models import User

_EMAIL_SEQUENCE = count(1)


def _build_email(prefix: str) -> str:
    return f"{prefix}{next(_EMAIL_SEQUENCE)}@test.local"


def create_test_user(
    *,
    email: str | None = None,
    email_prefix: str = "user",
    role: str = User.Role.STUDENT,
    password: str = "password123",
    **overrides: Any,
) -> User:
    """QnA 테스트 공통 유저 생성 헬퍼."""
    defaults: dict[str, Any] = {
        "name": "테스트유저",
        "nickname": "테스터",
        "phone_number": "01000000000",
        "gender": User.Gender.MALE,
        "birthday": "2000-01-01",
        "is_active": True,
        "role": role,
    }
    defaults.update(overrides)
    resolved_email = email or _build_email(email_prefix)
    return User.objects.create_user(email=resolved_email, password=password, **defaults)


def create_student_user(*, email: str | None = None, **overrides: Any) -> User:
    defaults = {"name": "수강생", "nickname": "수강생"}
    defaults.update(overrides)
    return create_test_user(email=email, email_prefix="student", role=User.Role.STUDENT, **defaults)


def create_general_user(*, email: str | None = None, **overrides: Any) -> User:
    defaults = {"name": "일반유저", "nickname": "일반유저"}
    defaults.update(overrides)
    return create_test_user(email=email, email_prefix="user", role=User.Role.USER, **defaults)


def create_admin_user(*, email: str | None = None, **overrides: Any) -> User:
    defaults = {"name": "관리자", "nickname": "관리자"}
    defaults.update(overrides)
    return create_test_user(email=email, email_prefix="admin", role=User.Role.ADMIN, **defaults)


def create_ta_user(*, email: str | None = None, **overrides: Any) -> User:
    defaults = {"name": "조교", "nickname": "조교"}
    defaults.update(overrides)
    return create_test_user(email=email, email_prefix="ta", role=User.Role.TA, **defaults)


def create_lc_user(*, email: str | None = None, **overrides: Any) -> User:
    defaults = {"name": "러닝코치", "nickname": "러닝코치"}
    defaults.update(overrides)
    return create_test_user(email=email, email_prefix="lc", role=User.Role.LC, **defaults)


def create_om_user(*, email: str | None = None, **overrides: Any) -> User:
    defaults = {"name": "운영매니저", "nickname": "운영매니저"}
    defaults.update(overrides)
    return create_test_user(email=email, email_prefix="om", role=User.Role.OM, **defaults)
