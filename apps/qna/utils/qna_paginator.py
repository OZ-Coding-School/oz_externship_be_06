# File Path: apps/qna/utils/qna_paginator.py
from __future__ import annotations

from typing import Any, Type

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import BasePagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from apps.core.utils.pagination import AdminCategoryPagination, QnaPagination
from apps.qna.constants import ErrorMessages
from apps.qna.exceptions.base import QnaBaseException


class QnaBaseListPaginator:
    """
    QnA, QnA-Admin Base 페이지네이션 응답 빌더
    """

    pagination_class: Type[BasePagination] = QnaPagination

    @classmethod
    def get_paginated_data_response(
        cls, queryset: Any, request: Request, serializer_class: Type[Serializer[Any]], view: Any = None
    ) -> Response:
        """QuerySet 기반 페이지네이션 응답 객체 생성 공통 로직"""
        # 클래스에 정의된 페이지네이션 인스턴스 생성
        instance = cls.pagination_class()

        try:
            # 데이터 분할 및 page_number 검증
            page = instance.paginate_queryset(queryset, request, view=view)

            # 페이지네이션이 활성화된 경우
            if page is not None:
                serializer = serializer_class(page, many=True)
                return instance.get_paginated_response(list(serializer.data))

            # 페이지네이션이 적용되지 않는 경우 (전체 반환)
            serializer = serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except NotFound:
            raise QnaBaseException(detail=ErrorMessages.NOT_FOUND_PAGE, status_code=status.HTTP_404_NOT_FOUND)


class QuestionListPaginator(QnaBaseListPaginator):
    """일반 유저용 질문 목록 페이지네이터"""

    pagination_class = QnaPagination


class AdminCategoryListPaginator(QnaBaseListPaginator):
    """어드민용 카테고리 목록 페이지네이터"""

    pagination_class = AdminCategoryPagination
