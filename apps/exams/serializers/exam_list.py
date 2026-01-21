from rest_framework import serializers
from apps.exams.models.exam_submissions import ExamSubmission

class ExamListSerializer(serializers.ModelSerializer):
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

    def get_exam(self, obj):
        e = obj.deployment.exam
        s = e.subject
        return {
            "id": e.id,
            "title": e.title,
            "thumbnail_img_url": e.thumbnail_img_url,
            "subject": {
                "id": s.id,
                "title": s.title,
                "thumbnail_img_url": s.thumbnail_img_url,
            },
        }

    def get_question_count(self, obj):
        e = obj.deployment.exam
        return e.questions.count() if hasattr(e, "questions") else 0

    def get_total_score(self, obj):
        e = obj.deployment.exam
        return getattr(e, "total_score", 0)

    def get_exam_info(self, obj):
        status = "pending" if obj.answers_json == {} else "done"
        return {
            "status": status,
            "score": obj.score,
            "correct_answer_count": obj.correct_answer_count,
        }

    def get_is_done(self, obj):
        return obj.answers_json != {}