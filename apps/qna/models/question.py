from __future__ import annotations

from typing import Optional

from django.db import models

from apps.core.models import TimeStampModel
from apps.qna.models.question_category import QuestionCategory
from apps.core.utils.content_parser import ContentParser
from apps.users.models import User


class Question(TimeStampModel):
    category = models.ForeignKey(
        QuestionCategory, on_delete=models.PROTECT, related_name="questions", verbose_name="카테고리"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions", verbose_name="작성자")
    title = models.CharField(max_length=50, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    view_count = models.PositiveIntegerField(default=0, verbose_name="조회수")

    is_ai_answered = models.BooleanField(default=False, verbose_name="AI 답변 여부")
    is_staff_answered = models.BooleanField(default=False, verbose_name="운영진 답변 여부")

    class Meta:
        db_table = "question"
        verbose_name = "질문"
        verbose_name_plural = "질문 목록"

    def __str__(self) -> str:
        return f"[{self.pk}] {self.title}"

    @property
    def content_preview(self) -> str:
        """본문의 마크다운/HTML 태그를 제거한 미리보기 텍스트 반환"""
        limit = 50
        return ContentParser.extract_content_preview(self.content, limit) or ""

    @property
    def thumbnail_img_url(self) -> Optional[str]:
        """본문 내 첫 번째 이미지 URL 반환"""
        return ContentParser.extract_thumbnail_img_url(self.content)
