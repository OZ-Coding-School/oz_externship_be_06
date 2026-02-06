from typing import Any, Type

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from apps.core.utils.pagination import QnaPagination
from apps.qna.constants import ErrorMessages
from apps.qna.exceptions import QnaBaseException


class QnaPaginator:
    """
    QnA, QnA-Admin 페이지네이션 응답 빌더
    """

    @classmethod
    def get_paginated_data_response(
        cls, queryset: Any, request: Any, serializer_class: Type[Serializer[Any]], view: Any = None
    ) -> Response:
        """QuerySet 기반 페이지네이션 응답 객체 생성"""
        # core에 정의된 페이지네이션 인스턴스 생성
        instance = QnaPagination()

        try:
            # 데이터 분할 및 page_number 검증
            page = instance.paginate_queryset(queryset, request, view=view)

            # 페이지네이션이 활성화된 경우 (page가 리스트인 경우)
            if page is not None:
                serializer = serializer_class(page, many=True)
                return instance.get_paginated_response(serializer.data)

            # 페이지네이션이 적용되지 않는 경우 (전체 반환)
            serializer = serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except NotFound:
            raise QnaBaseException(detail=ErrorMessages.NOT_FOUND_PAGE, status_code=status.HTTP_404_NOT_FOUND)
