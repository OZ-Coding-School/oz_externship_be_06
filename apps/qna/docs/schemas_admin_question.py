from drf_spectacular.utils import OpenApiResponse, extend_schema

from apps.core.serializers import ErrorResponseSerializer
from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.serializers.admin.question.response import (
    AdminQuestionDetailResponseSerializer,
)

ADMIN_QUESTION_DETAIL_SCHEMA = extend_schema(
    tags=["admin_qna"],
    summary="어드민 질문 상세 조회 API",
    description=ApiDescriptions.ADMIN_QUESTION_DETAIL,
    responses={
        200: OpenApiResponse(
            description="OK",
            response=AdminQuestionDetailResponseSerializer,
            examples=[SuccessResponseExamples.ADMIN_QUESTION_DETAIL],
        ),
        400: OpenApiResponse(
            description="Bad Request",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_QUESTION_DETAIL_400],
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_QUESTION_DETAIL_401],
        ),
        403: OpenApiResponse(
            description="Forbidden",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_QUESTION_DETAIL_403],
        ),
        404: OpenApiResponse(
            description="Not Found",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_QUESTION_DETAIL_404],
        ),
    },
)
