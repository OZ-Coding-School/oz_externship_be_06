from rest_framework import serializers

from apps.qna.models import Answer, AnswerComment
from apps.qna.serializers.common import AuthorSerializer


class AnswerCommentSerializer(serializers.ModelSerializer[AnswerComment]):
    """
    답변 댓글 상세 정보 시리얼라이저
    """

    author = AuthorSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = AnswerComment
        fields = ["id", "content", "created_at", "author"]


class AnswerSerializer(serializers.ModelSerializer[Answer]):
    """
    질문 상세 조회 내 답변 목록용 시리얼라이저
    """

    author = AuthorSerializer(read_only=True)
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
