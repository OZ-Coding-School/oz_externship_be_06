import json
from typing import Any

from rest_framework import serializers

from apps.courses.models.subjects import Subject
from apps.exams.models import Exam, ExamQuestion


class SubjectSerializer(serializers.ModelSerializer[Subject]):
    class Meta:
        model = Subject
        fields = ["id", "title"]


class AdminExamQuestionSerializer(serializers.ModelSerializer[ExamQuestion]):
    question_id = serializers.IntegerField(source="id", read_only=True)
    options = serializers.SerializerMethodField()
    correct_answer = serializers.JSONField(source="answer", read_only=True)

    class Meta:
        model = ExamQuestion
        fields = [
            "question_id",
            "type",
            "question",
            "prompt",
            "point",
            "options",
            "correct_answer",
            "explanation",
        ]

    def get_options(self, obj: ExamQuestion) -> Any:
        if not obj.options_json:
            return []
        try:
            return json.loads(obj.options_json)
        except json.JSONDecodeError:
            return []


class AdminExamDetailSerializer(serializers.ModelSerializer[Exam]):
    subject = SubjectSerializer(read_only=True)
    questions = AdminExamQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "subject",
            "questions",
            "thumbnail_img_url",
            "created_at",
            "updated_at",
        ]
