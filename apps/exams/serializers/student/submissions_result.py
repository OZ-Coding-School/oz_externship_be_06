from typing import Any, NotRequired, TypedDict

from rest_framework import serializers

from apps.exams.models import Exam, ExamQuestion, ExamSubmission
from apps.exams.services.answers_json import normalize_answers_json


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
        return max(0, int(seconds // 60))

    def _answers_map(self, obj: ExamSubmission) -> dict[int, object]:
        normalized = normalize_answers_json(obj.answers_json)
        m: dict[int, object] = {}
        for item in normalized:
            qid = item.get("question_id")
            if qid is None:
                continue
            try:
                qid_int = int(qid)
            except (TypeError, ValueError):
                continue
            m[qid_int] = item.get("submitted_answer")
        return m

    class _QuestionSnapshot(TypedDict):
        question_id: int
        type: str
        question: str
        answer: Any
        point: int
        prompt: NotRequired[str | None]
        blank_count: NotRequired[int | None]
        options: NotRequired[list[Any] | None]
        explanation: NotRequired[str]

    @staticmethod
    def _parse_snapshot(raw: Any) -> _QuestionSnapshot | None:
        if not isinstance(raw, dict):
            return None

        question_id = raw.get("question_id")
        q_type = raw.get("type")
        question = raw.get("question")
        answer = raw.get("answer")
        point = raw.get("point")

        if not isinstance(question_id, int) or question_id <= 0:
            return None
        if not isinstance(q_type, str) or not isinstance(question, str):
            return None
        if not isinstance(point, int):
            return None

        options = raw.get("options")
        if options is not None and not isinstance(options, list):
            return None

        return {
            "question_id": question_id,
            "type": q_type,
            "question": question,
            "answer": answer,
            "point": point,
            "prompt": raw.get("prompt"),
            "blank_count": raw.get("blank_count"),
            "options": options,
            "explanation": raw.get("explanation", ""),
        }

    def get_questions(self, obj: ExamSubmission) -> list[dict[str, Any]]:
        deployment = getattr(obj, "deployment", None)
        if not deployment:
            return []

        submitted_map = self._answers_map(obj)
        questions_snapshot = deployment.questions_snapshot_json
        if not isinstance(questions_snapshot, list):
            return []

        result = []
        for raw_question in questions_snapshot:
            question_data = self._parse_snapshot(raw_question)
            if question_data is None:
                continue
            question_id = question_data["question_id"]

            submitted = submitted_map.get(question_id)

            if submitted is None:
                submitted_norm = []
            elif isinstance(submitted, list):
                submitted_norm = submitted
            else:
                submitted_norm = [submitted]

            answer = question_data["answer"]
            if answer is None:
                answer_norm = []
            elif isinstance(answer, list):
                answer_norm = answer
            else:
                answer_norm = [answer]

            submitted_values = list(map(str, submitted_norm))
            answer_values = list(map(str, answer_norm))
            q_type = question_data["type"]
            if q_type in {ExamQuestion.TypeChoices.ORDERING, ExamQuestion.TypeChoices.FILL_IN_BLANK}:
                is_correct = submitted_values == answer_values
            else:
                is_correct = sorted(submitted_values) == sorted(answer_values)

            options = question_data.get("options") or []

            result.append(
                {
                    "id": question_id,
                    "question": question_data["question"],
                    "prompt": question_data.get("prompt"),
                    "blank_count": question_data.get("blank_count"),
                    "options": options,
                    "type": q_type,
                    "answer": answer_norm,
                    "point": question_data["point"],
                    "explanation": question_data.get("explanation", ""),
                    "is_correct": is_correct,
                    "submitted_answer": submitted_norm,
                }
            )

        return result
