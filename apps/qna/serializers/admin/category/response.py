from rest_framework import serializers

from apps.qna.models import QuestionCategory
from apps.qna.services.admin.category.command import DEPTH_TO_CATEGORY_TYPE


# ==============================================================================
# [POST] Admin Category Create Response
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
        return DEPTH_TO_CATEGORY_TYPE.get(obj.depth, "unknown")
