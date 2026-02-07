from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.qna.models import Answer, AnswerComment
from apps.qna.serializers.answer.common import AnswerAuthorSerializer


# ==============================================================================
# [GET] Question Detail
# /api/v1/qna/questions/{id}
# ==============================================================================
class AnswerCommentSerializer(serializers.ModelSerializer[AnswerComment]):
    """
    답변 댓글 상세 정보 시리얼라이저
    """

    author = AnswerAuthorSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = AnswerComment
        fields = ["id", "content", "created_at", "author"]


class AnswerSerializer(serializers.ModelSerializer[Answer]):
    """
    질문 상세 조회 내 답변 목록용 시리얼라이저
    """

    author = AnswerAuthorSerializer(read_only=True)
    comments = AnswerCommentSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Answer
        fields = [
            "id",
            "content",
            "created_at",
            "is_adopted",
            "author",
            "comments",
        ]


# ==============================================================================
# [GET] AI Answer
# /api/v1/qna/questions/{question_id}/ai-answer
# ==============================================================================
class AIAnswerResponseSerializer(serializers.Serializer[Any]):
    """
    AI 답변 생성 및 조회 응답 시리얼라이저
    """

    id = serializers.IntegerField(help_text="AI 답변 ID")
    question_id = serializers.IntegerField(source="question.id", help_text="질문 ID")
    output = serializers.CharField(help_text="AI가 생성한 답변 내용")
    using_model = serializers.CharField(help_text="사용된 AI 모델 명")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", help_text="생성 일시")


# ==============================================================================
# [ACTION RESPONSES] POST Success
# [POST] Answer Create
# /api/v1/qna/questions/{id}/answers
# ==============================================================================
class AnswerCreateResponseSerializer(serializers.ModelSerializer[Answer]):
    """
    답변 등록 응답 시리얼라이저
    """

    answer_id = serializers.IntegerField(source="id", help_text="답변 ID")
    question_id = serializers.IntegerField(source="question.id", help_text="질문 ID")
    author_id = serializers.IntegerField(source="author.id", help_text="작성자 ID")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", help_text="생성 일시")

    class Meta:
        model = Answer
        fields = ["answer_id", "question_id", "author_id", "created_at"]


# ==============================================================================
# [POST] Answer Adopt
# /api/v1/qna/answers/{answer_id}/accept
# ==============================================================================
class AnswerAdoptResponseSerializer(serializers.ModelSerializer[Answer]):
    """
    답변 채택 응답 시리얼라이저
    """

    question_id = serializers.IntegerField(source="question.id", help_text="질문 ID")
    answer_id = serializers.IntegerField(source="id", help_text="답변 ID")
    is_adopted = serializers.BooleanField(help_text="채택 여부")

    class Meta:
        model = Answer
        fields = ["question_id", "answer_id", "is_adopted"]
