from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.qna.models import Answer, AnswerComment


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
# [PUT] Answer Update
# /api/v1/qna/answers/{answer_id}
# ==============================================================================
class AnswerUpdateResponseSerializer(serializers.ModelSerializer[Answer]):
    """
    답변 수정 응답 시리얼라이저
    """

    answer_id = serializers.IntegerField(source="id", help_text="답변 ID")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", help_text="수정 일시")

    class Meta:
        model = Answer
        fields = ["answer_id", "updated_at"]


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


# ==============================================================================
# [POST] Answer Comment Create
# /api/v1/qna/answers/{answer_id}/comments
# ==============================================================================
class AnswerCommentCreateResponseSerializer(serializers.ModelSerializer[AnswerComment]):
    """
    답변 댓글 등록 응답 시리얼라이저
    """

    comment_id = serializers.IntegerField(source="id", help_text="댓글 ID")
    answer_id = serializers.IntegerField(source="answer.id", help_text="답변 ID")
    author_id = serializers.IntegerField(source="author.id", help_text="작성자 ID")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", help_text="생성 일시")

    class Meta:
        model = AnswerComment
        fields = ["comment_id", "answer_id", "author_id", "created_at"]
