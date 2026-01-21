from __future__ import annotations

from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class SimplePagePagination(PageNumberPagination):
    page_size = 10
    page_query_param = "page"

    def get_paginated_response(self, data: Any) -> Response:
        assert self.page is not None

        return Response(
            {
                "page": self.page.number,
                "has_next": self.page.has_next(),
                "results": data,
            }
        )
