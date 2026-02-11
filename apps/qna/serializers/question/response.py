from rest_framework import serializers

from apps.qna.models import Question, QuestionImage
from apps.qna.serializers.answer.common import AnswerSerializer
from apps.qna.serializers.question.common import (
    QuestionAuthorSerializer,
    QuestionCategoryListSerializer,
)


# ==============================================================================
# [POST] Question Create
# /api/v1/qna/questions/
# ==============================================================================
class QuestionCreateResponseSerializer(serializers.Serializer[Question]):
    """
    질문 등록 응답 시리얼라이저
    """

    message = serializers.CharField(default="질문이 성공적으로 등록되었습니다.")
    question_id = serializers.IntegerField(source="id")


# ==============================================================================
# [GET] Question List
# /api/v1/qna/questions
# ==============================================================================
class QuestionListSerializer(serializers.ModelSerializer[Question]):
    """
    질의응답 목록 조회 응답 시리얼라이저
    """

    category = QuestionCategoryListSerializer(read_only=True)
    author = QuestionAuthorSerializer(read_only=True)
    answer_count = serializers.IntegerField(read_only=True)

    content_preview = serializers.ReadOnlyField()
    thumbnail_img_url = serializers.ReadOnlyField()

    class Meta:
        model = Question
        fields = [
            "id",
            "category",
            "author",
            "title",
            "content_preview",
            "answer_count",
            "view_count",
            "created_at",
            "thumbnail_img_url",
        ]


# ==============================================================================
# [GET] Question Detail
# /api/v1/qna/questions/{question_id}
# ==============================================================================
class QuestionImageSerializer(serializers.ModelSerializer[QuestionImage]):
    """
    질문 이미지 시리얼라이저
    """

    class Meta:
        model = QuestionImage
        fields = ["id", "img_url"]


class QuestionDetailSerializer(serializers.ModelSerializer[Question]):
    """
    질문 상세 조회 응답 시리얼라이저
    """

    category = QuestionCategoryListSerializer(read_only=True)
    author = QuestionAuthorSerializer(read_only=True)
    images = QuestionImageSerializer(many=True, read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "title",
            "content",
            "category",
            "images",
            "view_count",
            "created_at",
            "author",
            "answers",
        ]


# ==============================================================================
# [PUT] Question Update
# /api/v1/qna/questions/{question_id}
# ==============================================================================
class QuestionUpdateResponseSerializer(serializers.ModelSerializer[Question]):
    """
    질문 수정 응답 시리얼라이저
    """

    question_id = serializers.IntegerField(source="id", help_text="질문 ID")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", help_text="수정 일시")

    class Meta:
        model = Question
        fields = ["question_id", "updated_at"]
