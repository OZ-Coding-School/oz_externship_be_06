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
