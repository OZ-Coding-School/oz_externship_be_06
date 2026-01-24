from typing import Any, Type

from rest_framework.response import Response
from rest_framework.serializers import Serializer

from apps.core.utils.pagination import QnAPagination


class QnAPaginator:
    """
    QnA 전용 페이지네이션 응답 빌더
    """

    @classmethod
    def get_paginated_data_response(
        cls, queryset: Any, request: Any, serializer_class: Type[Serializer[Any]], view: Any = None
    ) -> Response:
        """QuerySet 기반 페이지네이션 응답 객체 생성"""
        # core에 정의된 페이지네이션 인스턴스 생성
        instance = QnAPagination()
        page = instance.paginate_queryset(queryset, request, view=view)

        if page is not None:
            serializer = serializer_class(page, many=True)
            return instance.get_paginated_response(serializer.data)

        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)
