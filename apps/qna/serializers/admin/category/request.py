from typing import Any

from rest_framework import serializers

from apps.qna.constants import CATEGORY_LABELS, ErrorMessages


# ==============================================================================
# [POST] Admin Category
# /api/v1/admin/qna/categories
# ==============================================================================
class AdminCategoryCreateSerializer(serializers.Serializer[Any]):
    """
    어드민 카테고리 등록 요청 시리얼라이저
    - category_type: 카테고리 계층 (대분류, 중분류, 소분류)
    - name: 카테고리 이름
    - parent_id: 부모 카테고리 ID (중분류, 소분류의 경우 필수)
    """

    category_type = serializers.ChoiceField(
        choices=CATEGORY_LABELS,
        required=True,
        help_text="카테고리 타입 (대분류, 중분류, 소분류)",
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
        category_type = attrs["category_type"]
        parent_id = attrs.get("parent_id")

        if category_type == CATEGORY_LABELS[0] and parent_id is not None:
            raise serializers.ValidationError(f"{CATEGORY_LABELS[0]} 카테고리는 부모 카테고리를 지정할 수 없습니다.")

        if category_type != CATEGORY_LABELS[0] and parent_id is None:
            raise serializers.ValidationError(
                f"{CATEGORY_LABELS[1]}/{CATEGORY_LABELS[2]} 카테고리는 부모 카테고리가 필수입니다."
            )

        return attrs


# ==============================================================================
# [GET] Admin Category List
# /api/v1/admin/qna/categories
# ==============================================================================
class AdminCategoryListQuerySerializer(serializers.Serializer[Any]):
    """
    어드민 카테고리 목록 조회 요청 시리얼라이저
    """

    page = serializers.IntegerField(required=False, default=1, min_value=1)
    size = serializers.IntegerField(required=False, default=20, min_value=1)
    search_keyword = serializers.CharField(required=False, allow_blank=True)
    category_type = serializers.ChoiceField(choices=CATEGORY_LABELS, required=False)

    default_error_message = ErrorMessages.INVALID_ADMIN_CATEGORY_LIST
