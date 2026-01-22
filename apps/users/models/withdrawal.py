from __future__ import annotations

from datetime import date, timedelta

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampModel


# 회원 탈퇴 2주후 삭제
def two_weeks_later() -> date:
    return date.today() + timedelta(days=14)


class Withdrawal(TimeStampModel):
    class Reason(models.TextChoices):
        GRADUATION = "GRADUATION", "졸업 및 수료"
        TRANSFER = "TRANSFER", "편입 및 전학"
        NO_LONGER_NEEDED = "NO_LONGER_NEEDED", "더 이상 필요하지 않음"
        SERVICE_DISSATISFACTION = "SERVICE_DISSATISFACTION", "서비스 불만족"
        PRIVACY_CONCERN = "PRIVACY_CONCERN", "개인정보 보호 우려"
        OTHER = "OTHER", "기타"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="withdrawal",
        verbose_name="사용자",
    )
    reason = models.CharField(max_length=25, choices=Reason.choices)
    reason_detail = models.TextField()
    due_date = models.DateField(default=two_weeks_later)

    class Meta:
        db_table = "withdrawals"

    def __str__(self) -> str:
        return f"{self.user} - {self.get_reason_display()} ({self.due_date})"
