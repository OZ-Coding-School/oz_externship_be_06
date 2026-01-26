from rest_framework import serializers

from apps.qna.models import Answer, AnswerComment
from apps.qna.serializers.question.common import QuestionAuthorSerializer


class AnswerCommentSerializer(serializers.ModelSerializer[AnswerComment]):
    """
    답변 댓글 시리얼라이저
    """

    author = QuestionAuthorSerializer(read_only=True)

    class Meta:
        model = AnswerComment
        fields = ["id", "content", "created_at", "author"]


class AnswerSerializer(serializers.ModelSerializer[Answer]):
    """
    질문 답변 시리얼라이저 (댓글 포함)
    """

    author = QuestionAuthorSerializer(read_only=True)
    comments = AnswerCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = ["id", "content", "created_at", "is_adopted", "author", "comments"]
