from rest_framework import serializers

from apps.qna.models import Question


class AdminQuestionListResponseSerializer(serializers.ModelSerializer[Question]):
    """
    어드민 질의응답 목록 응답 시리얼라이저
    """

    question_id = serializers.IntegerField(source="id")
    category_path = serializers.SerializerMethodField()
    content_preview = serializers.CharField()
    nickname = serializers.CharField(source="author.nickname")
    has_answer = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Question
        fields = [
            "question_id",
            "title",
            "category_path",
            "content_preview",
            "nickname",
            "view_count",
            "has_answer",
            "created_at",
            "updated_at",
        ]

    def get_category_path(self, obj: Question) -> str:
        """대분류 > 중분류 > 소분류 형태의 카테고리 경로 반환"""
        names: list[str] = []
        category = obj.category
        while category:
            names.append(category.name)
            category = category.parent
        return " > ".join(reversed(names))

    def get_has_answer(self, obj: Question) -> bool:
        """답변 존재 여부 반환 (annotated answer_count 활용)"""
        return getattr(obj, "answer_count", 0) > 0
