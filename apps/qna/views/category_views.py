from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.qna.docs.schemas_category import CATEGORY_TREE_SCHEMA
from apps.qna.serializers.category.response import CategoryTreeResponseSerializer
from apps.qna.services.category.query import CategoryQueryService
from apps.qna.views.base_view import QnaBaseAPIView


class CategoryTreeAPIView(QnaBaseAPIView):
    """
    /api/v1/qna/categories
    [GET] 질의응답 카테고리 전체 계층 구조 조회
    """

    serializer_classes = {"GET": None}

    def get_permissions(self) -> list[Any]:
        method = self.request.method or ""
        if method == "GET":
            return [AllowAny()]
        raise MethodNotAllowed(method)

    # [GET] 카테고리 목록 조회
    @CATEGORY_TREE_SCHEMA
    def get(self, request: Request) -> Response:
        categories_tree = CategoryQueryService.get_category_tree()

        response_serializer = CategoryTreeResponseSerializer({"categories": categories_tree})
        return Response(response_serializer.data, status=status.HTTP_200_OK)
