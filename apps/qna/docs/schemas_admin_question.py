from drf_spectacular.utils import OpenApiResponse, extend_schema

from apps.core.serializers import ErrorResponseSerializer
from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.serializers.admin.question.request import (
    AdminQuestionListQuerySerializer,
)
from apps.qna.serializers.admin.question.response import (
    AdminQuestionDeleteResponseSerializer,
    AdminQuestionDetailResponseSerializer,
    AdminQuestionListResponseSerializer,
)

ADMIN_QUESTION_LIST_SCHEMA = extend_schema(
    tags=["admin_qna"],
    summary="어드민 질의응답 목록 조회 API",
    description=ApiDescriptions.ADMIN_QUESTION_LIST,
    parameters=[AdminQuestionListQuerySerializer],
    responses={
        200: OpenApiResponse(
            description="OK",
            response=AdminQuestionListResponseSerializer,
            examples=[SuccessResponseExamples.ADMIN_QUESTION_LIST],
        ),
        400: OpenApiResponse(
            description="Bad Request",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_QUESTION_LIST_400],
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_QUESTION_LIST_401],
        ),
        403: OpenApiResponse(
            description="Forbidden",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_QUESTION_LIST_403],
        ),
    },
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


ADMIN_QUESTION_DELETE_SCHEMA = extend_schema(
    tags=["admin_qna"],
    summary="어드민 질의응답 삭제 API",
    description=ApiDescriptions.ADMIN_QUESTION_DELETE,
    responses={
        200: OpenApiResponse(
            description="OK",
            response=AdminQuestionDeleteResponseSerializer,
            examples=[SuccessResponseExamples.ADMIN_QUESTION_DELETE],
        ),
        400: OpenApiResponse(
            description="Bad Request",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_QUESTION_DELETE_400],
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_QUESTION_DELETE_401],
        ),
        403: OpenApiResponse(
            description="Forbidden",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_QUESTION_DELETE_403],
        ),
        404: OpenApiResponse(
            description="Not Found",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ADMIN_QUESTION_DELETE_404],
        ),
    },
)
