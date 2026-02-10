from typing import Any

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnList

from apps.qna.models import QuestionCategory


# ==============================================================================
# [GET] Question category List
# /api/v1/qna/categories
# ==============================================================================
class CategoryTreeSerializer(serializers.Serializer[QuestionCategory]):
    """
    카테고리 계층 구조(Tree) 조회를 위한 재귀적 시리얼라이저
    """

    id = serializers.IntegerField(help_text="카테고리 ID")
    name = serializers.CharField(help_text="카테고리명")
    depth = serializers.IntegerField(help_text="계층 깊이 (0:대분류, 1:중분류, 2:소분류)")
    subcategories = serializers.SerializerMethodField(help_text="하위 카테고리 목록")

    def get_subcategories(self, obj: Any) -> ReturnList[Any]:
        """자식 노드를 재귀적으로 직렬화"""
        sub_data = getattr(obj, "subcategories", [])
        if hasattr(sub_data, "all"):
            sub_data = sub_data.all()

        return CategoryTreeSerializer(sub_data, many=True).data  # type: ignore


class CategoryTreeResponseSerializer(serializers.Serializer[Any]):
    """
    최상위 categories 키로 래핑하기 위한 응답 시리얼라이저
    """

    categories = CategoryTreeSerializer(many=True)
