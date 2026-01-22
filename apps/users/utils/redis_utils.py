from typing import Final, cast

from django.core.cache import cache

# 캐시 키 prefix
EMAIL_CODE_PREFIX: Final[str] = "email_code"
EMAIL_VERIFIED_PREFIX: Final[str] = "email_verified"

# 만료 시간 (초)
CODE_TIMEOUT: Final[int] = 300  # 5분
TOKEN_TIMEOUT: Final[int] = 3600  # 1시간


# 이메일 인증 코드
def save_email_code(email: str, code: str) -> None:
    cache.set(f"{EMAIL_CODE_PREFIX}:{email}", code, timeout=CODE_TIMEOUT)


def get_email_code(email: str) -> str | None:
    return cast(str | None, cache.get(f"{EMAIL_CODE_PREFIX}:{email}"))


def delete_email_code(email: str) -> None:
    cache.delete(f"{EMAIL_CODE_PREFIX}:{email}")


# 이메일 인증 토큰
def save_email_token(token: str, email: str) -> None:
    cache.set(f"{EMAIL_VERIFIED_PREFIX}:{token}", email, timeout=TOKEN_TIMEOUT)


def get_email_by_token(token: str) -> str | None:
    return cast(str | None, cache.get(f"{EMAIL_VERIFIED_PREFIX}:{token}"))


def delete_email_token(token: str) -> None:
    cache.delete(f"{EMAIL_VERIFIED_PREFIX}:{token}")
