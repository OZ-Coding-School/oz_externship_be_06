from typing import Final, cast

from django.core.cache import cache

# 만료 시간 (초)
CODE_TIMEOUT: Final[int] = 300  # 5분
TOKEN_TIMEOUT: Final[int] = 3600  # 1시간


# 공통 redis 캐시 항목
class CacheEntry:

    def __init__(self, prefix: str, timeout: int) -> None:
        self._prefix = prefix
        self._timeout = timeout

    def _key(self, identifier: str) -> str:
        return f"{self._prefix}:{identifier}"

    def save(self, identifier: str, value: str) -> None:
        cache.set(self._key(identifier), value, timeout=self._timeout)

    def get(self, identifier: str) -> str | None:
        return cast(str | None, cache.get(self._key(identifier)))

    def delete(self, identifier: str) -> None:
        cache.delete(self._key(identifier))


# 캐시 항목 인스턴스
email_code = CacheEntry("email_code", CODE_TIMEOUT)
email_token = CacheEntry("email_verified", TOKEN_TIMEOUT)
sms_code = CacheEntry("sms_code", CODE_TIMEOUT)
sms_token = CacheEntry("sms_verified", TOKEN_TIMEOUT)


# 이메일 인증 코드
def save_email_code(email: str, code: str) -> None:
    email_code.save(email, code)


def get_email_code(email: str) -> str | None:
    return email_code.get(email)


def delete_email_code(email: str) -> None:
    email_code.delete(email)


# 이메일 인증 토큰
def save_email_token(token: str, email: str) -> None:
    email_token.save(token, email)


def get_email_by_token(token: str) -> str | None:
    return email_token.get(token)


def delete_email_token(token: str) -> None:
    email_token.delete(token)


# SMS 인증 코드
def save_sms_code(phone_number: str, code: str) -> None:
    sms_code.save(phone_number, code)


def get_sms_code(phone_number: str) -> str | None:
    return sms_code.get(phone_number)


def delete_sms_code(phone_number: str) -> None:
    sms_code.delete(phone_number)


# SMS 인증 토큰
def save_sms_token(token: str, phone_number: str) -> None:
    sms_token.save(token, phone_number)


def get_phone_by_token(token: str) -> str | None:
    return sms_token.get(token)


def delete_sms_token(token: str) -> None:
    sms_token.delete(token)
