from drf_spectacular.utils import OpenApiResponse, extend_schema

from apps.core.serializers import ErrorResponseSerializer
from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.serializers.admin.answer.response import (
    AdminAnswerDeleteResponseSerializer,
)

ADMIN_ANSWER_DELETE_SCHEMA = extend_schema(
    tags=["admin_qna"],
    summary="어드민 답변 삭제 API",
    description=ApiDescriptions.ADMIN_ANSWER_DELETE,
    responses={
        200: OpenApiResponse(
            description="OK",
            response=AdminAnswerDeleteResponseSerializer,
            examples=[SuccessResponseExamples.ADMIN_ANSWER_DELETE],
        ),
        400: OpenApiResponse(
            description="Bad Request",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_ANSWER_DELETE_400],
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_ANSWER_DELETE_401],
        ),
        403: OpenApiResponse(
            description="Forbidden",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_ANSWER_DELETE_403],
        ),
        404: OpenApiResponse(
            description="Not Found",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_ANSWER_DELETE_404],
        ),
    },
)
