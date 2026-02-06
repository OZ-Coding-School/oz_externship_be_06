from typing import Any, Optional

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.utils.permissions import IsStaffRole
from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_request_examples import RequestBodyExamples
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.serializers.admin.category.request import AdminCategoryCreateSerializer
from apps.qna.serializers.admin.category.request import AdminCategoryListQuerySerializer
from apps.qna.serializers.admin.category.response import (
    AdminCategoryCreateResponseSerializer,
    AdminCategoryListResponseSerializer,
)
from apps.qna.services.admin.category.command import AdminCategoryCommandService
from apps.qna.services.admin.category.query import AdminCategoryQueryService
from apps.qna.utils.permissions import IsAdminOrStaff
from apps.qna.utils.qna_paginator import QnaPaginator
from apps.qna.views.base_view import QnaBaseAPIView


class AdminCategoriesAPIView(QnaBaseAPIView):
    """
    어드민 카테고리 등록 & 목록 조회 API View
    """

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), IsStaffRole()]

    serializer_class = {
        'POST': AdminCategoryCreateSerializer,
        'GET': AdminCategoryListQuerySerializer,
    }

    # 카테고리 등록
    # [POST] /api/v1/admin/qna/categories
    @extend_schema(
        tags=["admin_qna"],
        summary="어드민 카테고리 등록 API",
        description=ApiDescriptions.ADMIN_CATEGORY_CREATE,
        request=AdminCategoryCreateSerializer,
        examples=[RequestBodyExamples.ADMIN_CATEGORY_CREATE],
        responses={
            201: OpenApiResponse(
                description="Created",
                response=AdminCategoryCreateResponseSerializer,
                examples=[SuccessResponseExamples.ADMIN_CATEGORY_CREATE],
            ),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_CATEGORY_CREATE_400],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_CATEGORY_CREATE_401],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_CATEGORY_CREATE_403],
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_CATEGORY_CREATE_404],
            ),
            409: OpenApiResponse(
                description="Conflict",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_CATEGORY_CREATE_409],
            ),
        },
    )
    def post(self, request: Request) -> Response:
        """카테고리 생성"""
        serializer = AdminCategoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 서비스 호출
        category = AdminCategoryCommandService.create_category(data=serializer.validated_data)

        # 응답 출력
        response_serializer = AdminCategoryCreateResponseSerializer(category)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    # 카테고리 목록 조회
    # [GET] /api/v1/admin/qna/categories
    @extend_schema(
        tags=["admin_qna"],
        summary="카테고리 목록 조회 API",
        description=ApiDescriptions.ADMIN_CATEGORY_LIST,
        parameters=[AdminCategoryListQuerySerializer],
        responses={
            200: OpenApiResponse(
                description="OK",
                response=AdminCategoryListResponseSerializer,
                examples=[SuccessResponseExamples.ADMIN_CATEGORY_LIST],
            ),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_CATEGORY_LIST_400],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_CATEGORY_LIST_401],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_CATEGORY_LIST_403],
            ),
        },
    )
    def get(self, request: Request) -> Response:
        """카테고리 목록 조회"""
        # Request serializer
        request_serializer = AdminCategoryListQuerySerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)
        validated_data = request_serializer.validated_data

        # Service (query)
        category_list = AdminCategoryQueryService.get_category_list(data=validated_data)

        # Response serializer & Paginated response
        return QnaPaginator.get_paginated_data_response(
            queryset=category_list, request=request, serializer_class=AdminCategoryListResponseSerializer, view=self
        )



