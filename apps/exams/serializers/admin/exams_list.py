from rest_framework import serializers

from apps.exams.models import Exam


class AdminExamListItemSerializer(serializers.ModelSerializer[Exam]):
    exam_id = serializers.IntegerField(source="id", read_only=True)
    exam_title = serializers.CharField(source="title", read_only=True)

    subject_name = serializers.CharField(source="subject.name", read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    submit_count = serializers.IntegerField(read_only=True)

    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            "exam_id",
            "exam_title",
            "subject_name",
            "question_count",
            "submit_count",
            "created_at",
            "updated_at",
            "detail_url",
        ]

    def get_detail_url(self, obj: Exam) -> str:
        return f"/admin/exams/{obj.id}"
