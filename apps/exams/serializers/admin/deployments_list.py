from __future__ import annotations

from rest_framework import serializers

from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.models.exam_deployments import ExamDeployment
from apps.exams.models.exams import Exam


class AdminExamDeploymentCourseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ["id", "name", "tag"]


class AdminExamDeploymentCohortSerializer(serializers.ModelSerializer[Cohort]):
    display = serializers.SerializerMethodField()
    course = AdminExamDeploymentCourseSerializer(read_only=True)

    def get_display(self, obj: Cohort) -> str:
        return f"{obj.course.name} {obj.number}기"

    class Meta:
        model = Cohort
        fields = ["id", "number", "display", "course"]


class AdminExamDeploymentSubjectSerializer(serializers.ModelSerializer[Subject]):
    name = serializers.CharField(source="title")

    class Meta:
        model = Subject
        fields = ["id", "name"]


class AdminExamDeploymentExamSerializer(serializers.ModelSerializer[Exam]):
    class Meta:
        model = Exam
        fields = ["id", "title", "thumbnail_img_url"]


class AdminExamDeploymentListItemSerializer(serializers.ModelSerializer[ExamDeployment]):
    submit_count = serializers.IntegerField(read_only=True)
    avg_score = serializers.FloatField(read_only=True)
    status = serializers.SerializerMethodField()
    exam = AdminExamDeploymentExamSerializer(read_only=True)
    subject = AdminExamDeploymentSubjectSerializer(source="exam.subject", read_only=True)
    cohort = AdminExamDeploymentCohortSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    def get_status(self, obj: ExamDeployment) -> str:
        return obj.status.lower()

    class Meta:
        model = ExamDeployment
        fields = [
            "id",
            "submit_count",
            "avg_score",
            "status",
            "exam",
            "subject",
            "cohort",
            "created_at",
        ]
