from django.db import models

from apps.core.models import TimeStampModel


class ExamQuestion(TimeStampModel):
    class TypeChoices(models.TextChoices):
        FILL_IN_BLANK = "FILL_IN_BLANK", "빈칸 채우기"
        ORDERING = "ORDERING", "순서 정렬"
        MULTI_SELECT = "MULTI_SELECT", "다지선다"
        SHORT_ANSWER = "SHORT_ANSWER", "주관식 단답형"
        OX = "OX", "OX퀴즈"

    exam = models.ForeignKey("exams.Exam", on_delete=models.CASCADE, related_name="questions", verbose_name="시험")

    question = models.CharField(max_length=255, null=False, verbose_name="문항")
    prompt = models.TextField(null=True, blank=True, verbose_name="지문")
    blank_count = models.PositiveSmallIntegerField(null=False, default=0, verbose_name="빈칸 수")
    options_json = models.TextField(null=True, blank=True, verbose_name="보기(JSON)")
    type = models.CharField(
        max_length=20,
        choices=TypeChoices.choices,
        null=False,
        verbose_name="문항 유형",
    )
    answer = models.JSONField(null=False, verbose_name="정답(JSON)")
    point = models.PositiveSmallIntegerField(null=False, verbose_name="배점")
    explanation = models.TextField(null=False, verbose_name="해설")

    def __str__(self) -> str:
        return f"{self.exam.title} - {self.question}"

    class Meta:
        db_table = "exam_questions"
        verbose_name = "시험 문항"
        verbose_name_plural = "시험 문항 목록"
