from drf_spectacular.utils import OpenApiResponse, extend_schema

from apps.core.serializers import ErrorResponseSerializer
from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_request_examples import (
    QueryParameterExamples,
    RequestBodyExamples,
)
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.serializers.question.request import (
    QuestionCreateSerializer,
    QuestionQuerySerializer,
    QuestionUpdateRequestSerializer,
)
from apps.qna.serializers.question.response import (
    QuestionCreateResponseSerializer,
    QuestionDetailSerializer,
    QuestionListSerializer,
    QuestionUpdateResponseSerializer,
)

QUESTION_CREATE_SCHEMA = extend_schema(
    tags=["qna"],
    summary="질문 등록 API",
    description=ApiDescriptions.QUESTION_CREATE,
    request=QuestionCreateSerializer,
    examples=[RequestBodyExamples.QUESTION_CREATE],
    responses={
        201: OpenApiResponse(
            description="Created",
            response=QuestionCreateResponseSerializer,
            examples=[SuccessResponseExamples.QUESTION_CREATE],
        ),
        400: OpenApiResponse(
            description="Bad Request",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.QUESTION_CREATE_400],
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.QUESTION_CREATE_401],
        ),
        403: OpenApiResponse(
            description="Forbidden",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.QUESTION_CREATE_403],
        ),
    },
)


QUESTION_LIST_SCHEMA = extend_schema(
    tags=["qna"],
    summary="질문 목록 조회 API",
    description=ApiDescriptions.QUESTION_LIST,
    parameters=[QuestionQuerySerializer],
    examples=[QueryParameterExamples.QUESTION_LIST],
    responses={
        200: OpenApiResponse(
            description="OK",
            response=QuestionListSerializer(many=True),
            examples=[SuccessResponseExamples.QUESTION_LIST],
        ),
        400: OpenApiResponse(
            description="Bad Request",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.QUESTION_LIST_400],
        ),
        404: OpenApiResponse(
            description="Not Found",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.QUESTION_LIST_404],
        ),
    },
)


QUESTION_DETAIL_SCHEMA = extend_schema(
    tags=["qna"],
    summary="질문 상세 조회 API",
    description=ApiDescriptions.QUESTION_DETAIL,
    responses={
        200: OpenApiResponse(
            description="OK",
            response=QuestionDetailSerializer,
            examples=[SuccessResponseExamples.QUESTION_DETAIL],
        ),
        400: OpenApiResponse(
            description="Bad Request",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.QUESTION_DETAIL_400],
        ),
        404: OpenApiResponse(
            description="Not Found",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.QUESTION_DETAIL_404],
        ),
    },
)


QUESTION_UPDATE_SCHEMA = extend_schema(
    tags=["qna"],
    summary="질문 수정 API",
    description=ApiDescriptions.QUESTION_UPDATE,
    request=QuestionUpdateRequestSerializer,
    examples=[RequestBodyExamples.QUESTION_UPDATE],
    responses={
        200: OpenApiResponse(
            description="OK",
            response=QuestionUpdateResponseSerializer,
            examples=[SuccessResponseExamples.QUESTION_UPDATE],
        ),
        400: OpenApiResponse(
            description="Bad Request",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.QUESTION_UPDATE_400],
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.QUESTION_UPDATE_401],
        ),
        403: OpenApiResponse(
            description="Forbidden",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.QUESTION_UPDATE_403],
        ),
        404: OpenApiResponse(
            description="Not Found",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.QUESTION_UPDATE_404],
        ),
    },
)
