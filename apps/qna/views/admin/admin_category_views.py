from typing import Any

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.utils.permissions import IsStaffRole
from apps.qna.docs.schemas_admin_category import (
    ADMIN_CATEGORY_CREATE_SCHEMA,
    ADMIN_CATEGORY_LIST_SCHEMA,
)
from apps.qna.serializers.admin.category.request import (
    AdminCategoryCreateSerializer,
    AdminCategoryListQuerySerializer,
)
from apps.qna.serializers.admin.category.response import (
    AdminCategoryCreateResponseSerializer,
    AdminCategoryListResponseSerializer,
)
from apps.qna.services.admin.category.command import AdminCategoryCommandService
from apps.qna.services.admin.category.query import AdminCategoryQueryService
from apps.qna.utils.qna_paginator import AdminCategoryListPaginator as Paginator
from apps.qna.views.base_view import QnaBaseAPIView


class AdminCategoriesAPIView(QnaBaseAPIView):
    """
    어드민 카테고리 등록 & 목록 조회 API View
    """

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), IsStaffRole()]

    serializer_class = {
        "POST": AdminCategoryCreateSerializer,
        "GET": AdminCategoryListQuerySerializer,
    }

    # 카테고리 등록
    # [POST] /api/v1/admin/qna/categories
    @ADMIN_CATEGORY_CREATE_SCHEMA
    def post(self, request: Request) -> Response:
        """카테고리 생성"""
        # Request serializer
        serializer = AdminCategoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Service (command)
        category = AdminCategoryCommandService.create_category(data=serializer.validated_data)

        # Response serializer & response
        response_serializer = AdminCategoryCreateResponseSerializer(category)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    # 카테고리 목록 조회
    # [GET] /api/v1/admin/qna/categories
    @ADMIN_CATEGORY_LIST_SCHEMA
    def get(self, request: Request) -> Response:
        """카테고리 목록 조회"""
        # Request serializer
        request_serializer = AdminCategoryListQuerySerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)
        validated_data = request_serializer.validated_data

        # Service (query)
        category_list = AdminCategoryQueryService.get_category_list(data=validated_data)

        # Response serializer & Paginated response
        return Paginator.get_paginated_data_response(
            queryset=category_list, request=request, serializer_class=AdminCategoryListResponseSerializer, view=self
        )
