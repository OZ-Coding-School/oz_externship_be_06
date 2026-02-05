from typing import Any, cast

from django.db import transaction
from rest_framework import status

from apps.qna.constants import CATEGORY_LABELS, ErrorMessages
from apps.qna.exceptions import QnaBaseException
from apps.qna.models import QuestionCategory


class AdminCategoryCommandService:
    """
    어드민 카테고리 데이터 변경(CUD) 로직 처리 서비스
    """

    @staticmethod
    @transaction.atomic
    def create_category(data: dict[str, Any]) -> QuestionCategory:
        """
        새로운 카테고리 생성
        - Args:
            data (dict): category_type(str), name(str), parent_id(int|None)를 포함한 검증된 데이터
        - Returns:
            QuestionCategory: 생성된 카테고리 객체
        - Raises:
            QnaBaseException:
                400 - 부모 카테고리의 계층 불일치
                404 - 존재하지 않는 부모 카테고리
                409 - 동일한 이름의 카테고리 존재
        """

        # 입력받은 category_type을 비즈니스 로직용 depth로 변환
        category_type = data.get("category_type", "대분류")

        name: str = data["name"]
        parent_id: int | None = data.get("parent_id")

        # depth별 parent_id 유효성 검증
        parent = AdminCategoryCommandService._validate_parent(category_type, parent_id)

        # 동일 이름 중복 검사 (같은 부모 하위에서)
        AdminCategoryCommandService._validate_unique_subcategory_in_parent(name, parent)

        # 카테고리 생성
        category = QuestionCategory.objects.create(name=name, parent=parent)
        return category

    @staticmethod
    def _validate_parent(category_type: str, parent_id: int | None) -> QuestionCategory | None:
        """
        부모 카테고리의 존재 여부 및 계층 정합성 검증

        - 대분류(depth=0): parent 없음 (시리얼라이저에서 검증)
        - 중분류(depth=1): 부모는 대분류(depth=0)여야 함
        - 소분류(depth=2): 부모는 중분류(depth=1)여야 함
        """
        depth = CATEGORY_LABELS.index(category_type)

        if depth == 0:
            return None

        try:
            parent = QuestionCategory.objects.get(id=cast(int, parent_id))
        except QuestionCategory.DoesNotExist:
            raise QnaBaseException(
                detail=ErrorMessages.NOT_FOUND_ADMIN_CATEGORY_PARENT,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # 부모 depth가 현재 depth - 1인지 검증
        expected_parent_depth = depth - 1
        if parent.depth != expected_parent_depth:
            raise QnaBaseException(
                detail=f"부모 카테고리의 계층이 올바르지 않습니다. (기대: depth={expected_parent_depth}, 실제: depth={parent.depth})",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return parent

    @staticmethod
    def _validate_unique_subcategory_in_parent(name: str, parent: QuestionCategory | None) -> None:
        """같은 부모 카테고리 하위에서 동일한 이름의 카테고리가 있는지 검사"""
        if QuestionCategory.objects.filter(name=name, parent=parent).exists():
            raise QnaBaseException(
                detail=ErrorMessages.ALREADY_EXISTS_ADMIN_CATEGORY_NAME,
                status_code=status.HTTP_409_CONFLICT,
            )
