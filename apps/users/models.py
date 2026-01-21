from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampModel

# class User(AbstractUser):
#    pass


class VerificationChannel(models.TextChoices):
    EMAIL = "EMAIL", "이메일"
    PHONE = "PHONE", "휴대폰"


class VerificationPurpose(models.TextChoices):
    SIGNUP_EMAIL = "SIGNUP_EMAIL", "이메일 회원가입"
    SIGNUP_PHONE = "SIGNUP_PHONE", "휴대폰 회원가입"
    PASSWORD_RESET = "PASSWORD_RESET", "비밀번호 재설정"
    RESTORE_ACCOUNT = "RESTORE_ACCOUNT", "계정 복구"


class VerificationCode(TimeStampModel):
    """
    이메일/휴대폰 인증 코드 저장 테이블
    - EMAIL: code는 base62 문자열
    - PHONE: code는 6자리 난수 문자열 ("034921")
    """

    channel = models.CharField(
        max_length=10,
        choices=VerificationChannel.choices,
    )
    purpose = models.CharField(
        max_length=30,
        choices=VerificationPurpose.choices,
    )

    # User 생성 전에도 인증이 가능해야 해서 문자열로 저장
    target = models.CharField(max_length=255)
    code = models.CharField(max_length=64)

    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)

    attempt_count = models.PositiveSmallIntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "verification_code"
        indexes = [
            models.Index(fields=["channel", "purpose", "target", "consumed_at"]),
            models.Index(fields=["expires_at"]),
        ]
