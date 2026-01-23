from rest_framework import serializers

from apps.exams.models import ExamSubmission
from apps.exams.models import Exam

class ExamSimpleSerializer(serializers.ModelSerializer[Exam]):
    class Meta:
        model = Exam
        fields = ["id", "title", "thumbnail_img_url"]

class ExamSubmissionSerializer(serializers.ModelSerializer[ExamSubmission]):
    total_score = serializers.IntegerField(source="score", read_only=True)
    elapsed_time = serializers.SerializerMethodField()

    submitted_at = serializers.DateTimeField(source="created_at", read_only=True)

    exam = ExamSimpleSerializer(source="deployment.exam", read_only=True)

    questions = serializers.SerializerMethodField()


    class Meta:
        model = ExamSubmission
        fields = [
            "id",
            "submitter_id",
            "deployment_id",
            "exam",
            "questions",
            "cheating_count",
            "total_score",
            "correct_answer_count",
            "elapsed_time",
            "started_at",
            "submitted_at",
        ]
        read_only_fields = fields

    def get_elapsed_time(self, obj: ExamSubmission) -> int:
        seconds = (obj.created_at - obj.started_at).total_seconds()
        return int(seconds // 60)

    def _answers_map(self, obj: ExamSubmission) -> dict[int, object]:
        data = obj.answers_json

        if isinstance(data, list):
            m: dict[int, object] = {}
            for item in data:
                if not isinstance(item, dict):
                    continue
                qid = item.get("question_id")
                if qid is None:
                    continue
                try:
                    qid_int = int(qid)
                except (TypeError, ValueError):
                    continue
                m[qid_int] = item.get("submitted_answer")
            return m

        if isinstance(data, dict):
            if "answers" in data and isinstance(data["answers"], list):
                obj.answers_json = data["answers"]
                return self._answers_map(obj)

            m: dict[int, object] = {}
            for k, v in data.items():
                try:
                    qid_int = int(k)
                except (TypeError, ValueError):
                    continue
                m[qid_int] = v
            return m

        return {}

    def get_questions(self, obj: ExamSubmission):
        exam = getattr(obj.deployment, "exam", None)
        if not exam:
            return []

        submitted_map = self._answers_map(obj)
        qs = exam.questions.all()

        result = []
        for q in qs:
            submitted = submitted_map.get(q.id)

            if submitted is None:
                submitted_norm = []
            elif isinstance(submitted, list):
                submitted_norm = submitted
            else:
                submitted_norm = [submitted]

            answer = q.answer
            if answer is None:
                answer_norm = []
            elif isinstance(answer, list):
                answer_norm = answer
            else:
                answer_norm = [answer]

            is_correct = sorted(map(str, submitted_norm)) == sorted(map(str, answer_norm))

            options = []
            if q.options_json:
                try:
                    import json
                    options = json.loads(q.options_json)
                except Exception:
                    options = []

            result.append(
                {
                    "id": q.id,
                    "question": q.question,
                    "prompt": q.prompt,
                    "blank_count": q.blank_count,
                    "options": options,
                    "type": q.type,
                    "answer": answer_norm,
                    "point": q.point,
                    "explanation": q.explanation,
                    "is_correct": is_correct,
                    "submitted_answer": submitted_norm,
                }
            )

        return result