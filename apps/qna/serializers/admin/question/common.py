from rest_framework import serializers

from apps.qna.models import Answer
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
