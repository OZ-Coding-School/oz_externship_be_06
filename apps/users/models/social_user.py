from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampModel


class SocialUser(TimeStampModel):
    class Provider(models.TextChoices):
        NAVER = "NAVER", "네이버"
        KAKAO = "KAKAO", "카카오"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="social_users",
        verbose_name="사용자",
    )
    provider = models.CharField(
        max_length=10,
        choices=Provider.choices,
    )
    provider_id = models.CharField(
        max_length=255,
    )

    class Meta:
        db_table = "social_users"
        verbose_name = "소셜 유저"
        verbose_name_plural = "소셜 유저 목록"
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_id"],
                name="unique_provider_provider_id",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.get_provider_display()}"
