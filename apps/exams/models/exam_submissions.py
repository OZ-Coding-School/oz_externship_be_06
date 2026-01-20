from django.conf import settings
from django.db import models


class ExamSubmission(models.Model):
    submitter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_submissions",
        verbose_name="응시자",
    )
    deployment = models.ForeignKey(
        "exams.ExamDeployment",
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="시험 배포",
    )

    started_at = models.DateTimeField(null=False, verbose_name="응시 시작 일시")
    cheating_count = models.PositiveSmallIntegerField(null=False, default=0, verbose_name="부정행위 횟수")
    answers_json = models.JSONField(null=False, verbose_name="제출 답안(JSON)")
    score = models.PositiveSmallIntegerField(null=False, default=0, verbose_name="점수")
    correct_answer_count = models.PositiveSmallIntegerField(null=False, default=0, verbose_name="정답 수")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    def __str__(self) -> str:
        return f"{self.deployment.exam.title} - {self.submitter_id}"

    class Meta:
        db_table = "exam_submissions"
        verbose_name = "시험 제출"
        verbose_name_plural = "시험 제출 목록"
