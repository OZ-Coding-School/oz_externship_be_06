from __future__ import annotations

from typing import Any, List

from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response


class ChatbotSessionCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-created_at"
    cursor_query_param = "cursor"


class SimplePagePagination(PageNumberPagination):
    page_size = 10
    page_query_param = "page"
    page_size_query_param = "size"
    max_page_size = 100


class QnAPagination(PageNumberPagination):
    """
    질의응답 목록 조회를 위한 페이지네이션
    """

    page_size_query_param = "size"
    max_page_size = 100

    def get_paginated_response(self, data: Any) -> Response:
        """페이지네이션 응답 생성"""
        if self.page is None:
            return Response(data)

        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )


class AdminExamPagination(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "size"
    page_size = 10

    def get_paginated_response(self, data: List[Any]) -> Response:
        if self.page is None or self.request is None:
            return Response(data)

        return Response(
            {
                "page": self.page.number,
                "size": self.get_page_size(self.request),
                "total_count": self.page.paginator.count,
                "exams": data,
            }
        )
