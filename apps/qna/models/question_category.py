from __future__ import annotations

from django.db import models

from apps.core.models import TimeStampModel


class QuestionCategory(TimeStampModel):
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
        verbose_name="상위 카테고리",
    )
    name = models.CharField(max_length=15, verbose_name="카테고리명")

    class Meta:
        db_table = "question_category"
        verbose_name = "질문 카테고리"
        verbose_name_plural = "질문 카테고리 목록"

    def __str__(self) -> str:
        return self.name

    @property
    def depth(self) -> int:
        # - 0: 대분류, 1: 중분류, 2: 소분류
        d = 0
        curr = self.parent
        while curr:
            d += 1
            curr = curr.parent
        return d
