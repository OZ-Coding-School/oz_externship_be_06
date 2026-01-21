from __future__ import annotations

from typing import Any, TypedDict

from rest_framework import serializers

from apps.exams.models.exam_submissions import ExamSubmission


class SubjectDict(TypedDict):
    id: int
    title: str
    thumbnail_img_url: str | None


class ExamDict(TypedDict):
    id: int
    title: str
    thumbnail_img_url: str | None
    subject: SubjectDict


class ExamInfoDict(TypedDict):
    status: str
    score: int
    correct_answer_count: int


class ExamListSerializer(serializers.ModelSerializer[ExamSubmission]):
    submission_id = serializers.IntegerField(source="id", read_only=True)
    exam = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()
    total_score = serializers.SerializerMethodField()
    exam_info = serializers.SerializerMethodField()
    is_done = serializers.SerializerMethodField()

    class Meta:
        model = ExamSubmission
        fields = [
            "id",
            "submission_id",
            "exam",
            "question_count",
            "total_score",
            "exam_info",
            "is_done",
        ]

    def get_exam(self, obj: ExamSubmission) -> ExamDict:
        e = obj.deployment.exam
        s = e.subject
        # thumbnail_img_url 타입이 확실치 않아서 None 가능성 포함(보수적으로)
        return {
            "id": int(e.id),
            "title": str(e.title),
            "thumbnail_img_url": getattr(e, "thumbnail_img_url", None),
            "subject": {
                "id": int(s.id),
                "title": str(s.title),
                "thumbnail_img_url": getattr(s, "thumbnail_img_url", None),
            },
        }

    def get_question_count(self, obj: ExamSubmission) -> int:
        e = obj.deployment.exam
        # 보통 related_name="questions"면 항상 존재하지만, 기존 로직 유지
        if hasattr(e, "questions"):
            return int(e.questions.count())
        return 0

    def get_total_score(self, obj: ExamSubmission) -> int:
        e = obj.deployment.exam
        return int(getattr(e, "total_score", 0))

    def get_exam_info(self, obj: ExamSubmission) -> ExamInfoDict:
        status = "pending" if obj.answers_json == {} else "done"
        return {
            "status": status,
            "score": int(obj.score),
            "correct_answer_count": int(obj.correct_answer_count),
        }

    def get_is_done(self, obj: ExamSubmission) -> bool:
        return bool(obj.answers_json and obj.answers_json != {})
