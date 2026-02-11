from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.qna.constants import CATEGORY_LABELS
from apps.qna.models import QuestionCategory


# ==============================================================================
# [POST] Admin Category Create
# /api/v1/admin/qna/categories
# ==============================================================================
class AdminCategoryCreateResponseSerializer(serializers.ModelSerializer[QuestionCategory]):
    """
    어드민 카테고리 등록 응답 시리얼라이저
    """

    category_id = serializers.IntegerField(source="id", help_text="카테고리 ID")
    name = serializers.CharField(help_text="카테고리 이름")
    category_type = serializers.SerializerMethodField(help_text="카테고리 종류 (large, medium, small)")
    parent_id = serializers.IntegerField(source="parent.id", default=None, help_text="부모 카테고리 ID")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", help_text="생성일시")

    class Meta:
        model = QuestionCategory
        fields = ["category_id", "name", "category_type", "parent_id", "created_at"]

    def get_category_type(self, obj: QuestionCategory) -> str:
        """depth 프로퍼티를 기반으로 category_type 문자열 반환"""
        return CATEGORY_LABELS[obj.depth]


# ==============================================================================
# [GET] Admin Category List
# /api/v1/admin/qna/categories
# ==============================================================================
class AdminCategoryListResponseSerializer(serializers.ModelSerializer[QuestionCategory]):
    """
    어드민 카테고리 목록 응답 시리얼라이저
    """

    category_id = serializers.IntegerField(source="id")
    category_type = serializers.SerializerMethodField()
    parent_category = serializers.SerializerMethodField()
    child_categories = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = QuestionCategory
        fields = [
            "category_id",
            "name",
            "category_type",
            "parent_category",
            "child_categories",
            "created_at",
            "updated_at",
        ]

    def get_category_type(self, obj: QuestionCategory) -> str:
        return CATEGORY_LABELS[obj.depth]

    def get_parent_category(self, obj: QuestionCategory) -> str:
        if obj.parent:
            return obj.parent.name
        return ""

    def get_child_categories(self, obj: QuestionCategory) -> list[str]:
        children = getattr(obj, "subcategories", None)
        if children:
            return [child.name for child in children.all()]
        return []


# ==============================================================================
# [DELETE] Admin Category Delete
# /api/v1/admin/qna/categories/{category_id}
# ==============================================================================
class AdminCategoryDeleteResponseSerializer(serializers.Serializer[Any]):
    """
    어드민 카테고리 삭제 응답 시리얼라이저
    """

    category_id = serializers.IntegerField()
    category_type = serializers.CharField()
    migrated_question_count = serializers.IntegerField()
