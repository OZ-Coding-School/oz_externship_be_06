from typing import Any, Optional

from rest_framework import serializers

from apps.qna.models import Answer, Question
from apps.qna.utils.course_info import get_course_generation, get_role_title
from apps.qna.utils.model_types import User


class AdminQuestionAuthorSerializer(serializers.Serializer[User]):
    """
    어드민 질문 상세 조회 - 질문 작성자 시리얼라이저
    """

    profile_img_url = serializers.CharField(allow_null=True)
    nickname = serializers.CharField()
    course_generation = serializers.SerializerMethodField()

    def get_course_generation(self, obj: User) -> str:
        return get_course_generation(obj)


class AdminAnswerAuthorSerializer(serializers.Serializer[User]):
    """
    어드민 질문 상세 조회 - 답변 작성자 시리얼라이저
    """

    profile_img_url = serializers.CharField(allow_null=True)
    nickname = serializers.CharField()
    role_title = serializers.SerializerMethodField()
    course_generation = serializers.SerializerMethodField()

    def get_role_title(self, obj: User) -> str:
        return get_role_title(obj)

    def get_course_generation(self, obj: User) -> str:
        return get_course_generation(obj)


class AdminAnswerSerializer(serializers.ModelSerializer[Answer]):
    """
    어드민 질문 상세 조회 - 답변 시리얼라이저
    """

    answer_id = serializers.IntegerField(source="id")
    author = AdminAnswerAuthorSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Answer
        fields = [
            "answer_id",
            "author",
            "content",
            "is_adopted",
            "created_at",
            "updated_at",
        ]


class AdminQuestionDetailResponseSerializer(serializers.ModelSerializer[Question]):
    """
    어드민 질문 상세 조회 응답 시리얼라이저
    """

    question_id = serializers.IntegerField(source="id")
    author = AdminQuestionAuthorSerializer(read_only=True)
    img_url = serializers.SerializerMethodField()
    has_answer = serializers.SerializerMethodField()
    answers = AdminAnswerSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Question
        fields = [
            "question_id",
            "title",
            "content",
            "img_url",
            "author",
            "view_count",
            "has_answer",
            "created_at",
            "updated_at",
            "answers",
        ]

    def get_img_url(self, obj: Question) -> list[Optional[str]]:
        return [image.img_url for image in obj.images.all()]

    def get_has_answer(self, obj: Any) -> bool:
        return bool(obj.answers.exists())
