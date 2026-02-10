from drf_spectacular.utils import OpenApiResponse, extend_schema

from apps.core.serializers import ErrorResponseSerializer
from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.serializers.category.response import CategoryTreeResponseSerializer


CATEGORY_TREE_SCHEMA = extend_schema(
    tags=["qna"],
    summary="카테고리 계층 구조 조회",
    description=ApiDescriptions.CATEGORY_LIST,
    responses={
        200: OpenApiResponse(
            description="OK",
            response=CategoryTreeResponseSerializer,
            examples=[SuccessResponseExamples.CATEGORY_LIST],
        ),
        400: OpenApiResponse(
            description="Bad Request",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.CATEGORY_LIST_400],
        ),
    },
)
