from typing import Any

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.utils.permissions import IsStaffRole
from apps.qna.docs.schemas_admin_category import (
    ADMIN_CATEGORY_CREATE_SCHEMA,
    ADMIN_CATEGORY_DELETE_SCHEMA,
    ADMIN_CATEGORY_LIST_SCHEMA,
)
from apps.qna.serializers.admin.category.request import (
    AdminCategoryCreateSerializer,
    AdminCategoryListQuerySerializer,
)
from apps.qna.serializers.admin.category.response import (
    AdminCategoryCreateResponseSerializer,
    AdminCategoryDeleteResponseSerializer,
    AdminCategoryListResponseSerializer,
)
from apps.qna.services.admin.category.command import AdminCategoryCommandService
from apps.qna.services.admin.category.query import AdminCategoryQueryService
from apps.qna.utils.qna_paginator import AdminCategoryListPaginator as Paginator
from apps.qna.views.base_view import QnaBaseAPIView


class AdminCategoriesAPIView(QnaBaseAPIView):
    """
    /api/v1/admin/qna/categories
    [POST] 카테고리 등록
    [GET] 카테고리 목록 조회
    """

    serializer_classes = {
        "POST": AdminCategoryCreateSerializer,
        "GET": AdminCategoryListQuerySerializer,
    }

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), IsStaffRole()]

    # [POST] 카테고리 등록
    @ADMIN_CATEGORY_CREATE_SCHEMA
    def post(self, request: Request) -> Response:
        request_serializer = AdminCategoryCreateSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        category = AdminCategoryCommandService.create_category(data=request_serializer.validated_data)

        response_serializer = AdminCategoryCreateResponseSerializer(category)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    # [GET] 카테고리 목록 조회
    @ADMIN_CATEGORY_LIST_SCHEMA
    def get(self, request: Request) -> Response:
        query_serializer = AdminCategoryListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        category_list = AdminCategoryQueryService.get_category_list(filters=query_serializer.validated_data)

        return Paginator.get_paginated_data_response(
            queryset=category_list, request=request, serializer_class=AdminCategoryListResponseSerializer, view=self
        )


class AdminCategoryDeleteAPIView(QnaBaseAPIView):
    """
    /api/v1/admin/qna/categories/{category_id}
    [DELETE] 어드민 카테고리 삭제
    """

    serializer_classes = {"DELETE": None}

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), IsStaffRole()]

    # [DELETE] 어드민 카테고리 삭제
    @ADMIN_CATEGORY_DELETE_SCHEMA
    def delete(self, request: Request, category_id: int) -> Response:
        delete_summary = AdminCategoryCommandService.delete_category(category_id=category_id)

        response_serializer = AdminCategoryDeleteResponseSerializer(delete_summary)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
