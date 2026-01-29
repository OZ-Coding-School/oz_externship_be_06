from __future__ import annotations

from rest_framework import serializers

from apps.courses.models.subjects import Subject
from apps.exams.models.exam_deployments import ExamDeployment
from apps.exams.models.exams import Exam


class ExamListQuerySerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["all", "done", "pending"], required=False, default="all")


class SubjectSerializer(serializers.ModelSerializer[Subject]):
    class Meta:
        model = Subject
        fields = ["id", "title", "thumbnail_img_url"]


class ExamSerializer(serializers.ModelSerializer[Exam]):
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = Exam
        fields = ["id", "title", "thumbnail_img_url", "subject"]


class ExamInfoSerializer(serializers.Serializer[ExamDeployment]):
    status = serializers.CharField(source="exam_status")
    score = serializers.IntegerField()
    correct_answer_count = serializers.IntegerField()


class ExamDeploymentListSerializer(serializers.ModelSerializer[ExamDeployment]):
    submission_id = serializers.IntegerField(read_only=True, allow_null=True)

    exam = ExamSerializer(read_only=True)

    question_count = serializers.IntegerField(read_only=True)
    total_score = serializers.IntegerField(read_only=True)
    is_done = serializers.BooleanField(read_only=True)

    exam_info = ExamInfoSerializer(source="*", read_only=True)

    duration_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = ExamDeployment
        fields = [
            "id",
            "submission_id",
            "exam",
            "question_count",
            "total_score",
            "exam_info",
            "is_done",
            "duration_time",
        ]
