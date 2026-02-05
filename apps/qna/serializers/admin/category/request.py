from typing import Any

from rest_framework import serializers

from apps.qna.constants import ErrorMessages


# ==============================================================================
# [POST] Admin Category Create
# /api/v1/admin/qna/categories
# ==============================================================================
class AdminCategoryCreateSerializer(serializers.Serializer[Any]):
    """
    어드민 카테고리 등록 요청 시리얼라이저

    - depth: 카테고리 계층 (0: 대분류, 1: 중분류, 2: 소분류)
    - name: 카테고리 이름
    - parent_id: 부모 카테고리 ID (중분류, 소분류의 경우 필수)
    """

    depth = serializers.ChoiceField(
        choices=[0, 1, 2],
        required=True,
        help_text="카테고리 계층 (0: 대분류, 1: 중분류, 2: 소분류)",
    )
    name = serializers.CharField(
        max_length=15,
        required=True,
        help_text="카테고리 이름",
    )
    parent_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        default=None,
        help_text="부모 카테고리 ID (중분류, 소분류의 경우 필수)",
    )

    default_error_message = ErrorMessages.INVALID_ADMIN_CATEGORY_CREATE

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """depth와 parent_id 조합의 입력 형태 검증"""
        depth = attrs["depth"]
        parent_id = attrs.get("parent_id")

        if depth == 0 and parent_id is not None:
            raise serializers.ValidationError("대분류 카테고리는 부모 카테고리를 지정할 수 없습니다.")

        if depth != 0 and parent_id is None:
            raise serializers.ValidationError("중분류/소분류 카테고리는 부모 카테고리가 필수입니다.")

        return attrs
