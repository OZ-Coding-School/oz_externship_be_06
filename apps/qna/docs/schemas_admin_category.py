from drf_spectacular.utils import OpenApiResponse, extend_schema

from apps.core.serializers import ErrorResponseSerializer
from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_request_examples import RequestBodyExamples
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.serializers.admin.category.request import (
    AdminCategoryCreateSerializer,
    AdminCategoryListQuerySerializer,
)
from apps.qna.serializers.admin.category.response import (
    AdminCategoryCreateResponseSerializer,
    AdminCategoryListResponseSerializer,
)


ADMIN_CATEGORY_CREATE_SCHEMA = extend_schema(
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
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_CATEGORY_CREATE_400],
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_CATEGORY_CREATE_401],
        ),
        403: OpenApiResponse(
            description="Forbidden",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_CATEGORY_CREATE_403],
        ),
        404: OpenApiResponse(
            description="Not Found",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_CATEGORY_CREATE_404],
        ),
        409: OpenApiResponse(
            description="Conflict",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_CATEGORY_CREATE_409],
        ),
    },
)


ADMIN_CATEGORY_LIST_SCHEMA = extend_schema(
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
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_CATEGORY_LIST_400],
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_CATEGORY_LIST_401],
        ),
        403: OpenApiResponse(
            description="Forbidden",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_CATEGORY_LIST_403],
        ),
    },
)
