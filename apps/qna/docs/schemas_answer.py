from drf_spectacular.utils import OpenApiResponse, extend_schema

from apps.core.serializers import ErrorResponseSerializer
from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_request_examples import RequestBodyExamples
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.serializers.answer.request import (
    AnswerCommentCreateSerializer,
    AnswerCreateSerializer,
    AnswerUpdateSerializer,
)
from apps.qna.serializers.answer.response import (
    AIAnswerResponseSerializer,
    AnswerAdoptResponseSerializer,
    AnswerCommentCreateResponseSerializer,
    AnswerCreateResponseSerializer,
    AnswerUpdateResponseSerializer,
)

AI_ANSWER_GENERATE_SCHEMA = extend_schema(
    tags=["qna"],
    summary="AI 답변 생성 API",
    description=ApiDescriptions.AI_ANSWER_GENERATE,
    request=None,
    responses={
        201: OpenApiResponse(
            description="Created",
            response=AIAnswerResponseSerializer,
            examples=[SuccessResponseExamples.AI_ANSWER_GENERATE],
        ),
        400: OpenApiResponse(
            description="Bad Request",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.AI_ANSWER_GENERATE_400],
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.AI_ANSWER_GENERATE_401],
        ),
        404: OpenApiResponse(
            description="Not Found",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.AI_ANSWER_GENERATE_404],
        ),
        409: OpenApiResponse(
            description="Conflict",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.AI_ANSWER_GENERATE_409],
        ),
    },
)


ANSWER_CREATE_SCHEMA = extend_schema(
    tags=["qna"],
    summary="답변 등록 API",
    description=ApiDescriptions.ANSWER_CREATE,
    request=AnswerCreateSerializer,
    examples=[RequestBodyExamples.ANSWER_CREATE],
    responses={
        201: OpenApiResponse(
            description="답변 등록 성공",
            response=AnswerCreateResponseSerializer,
            examples=[SuccessResponseExamples.ANSWER_CREATE],
        ),
        400: OpenApiResponse(
            description="Bad Request",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_CREATE_400],
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_CREATE_401],
        ),
        403: OpenApiResponse(
            description="Forbidden",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_CREATE_403],
        ),
        404: OpenApiResponse(
            description="Not Found",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_CREATE_404],
        ),
    },
)


ANSWER_UPDATE_SCHEMA = extend_schema(
    tags=["qna"],
    summary="답변 수정 API",
    description=ApiDescriptions.ANSWER_UPDATE,
    request=AnswerUpdateSerializer,
    examples=[RequestBodyExamples.ANSWER_UPDATE],
    responses={
        200: OpenApiResponse(
            description="답변 수정 성공",
            response=AnswerUpdateResponseSerializer,
            examples=[SuccessResponseExamples.ANSWER_UPDATE],
        ),
        400: OpenApiResponse(
            description="Bad Request",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_UPDATE_400],
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_UPDATE_401],
        ),
        403: OpenApiResponse(
            description="Forbidden",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_UPDATE_403],
        ),
        404: OpenApiResponse(
            description="Not Found",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_UPDATE_404],
        ),
    },
)


ANSWER_ADOPT_SCHEMA = extend_schema(
    tags=["qna"],
    summary="답변 채택 API",
    description=ApiDescriptions.ANSWER_ADOPT,
    request=None,
    responses={
        200: OpenApiResponse(
            description="답변 채택 성공",
            response=AnswerAdoptResponseSerializer,
            examples=[SuccessResponseExamples.ANSWER_ADOPT],
        ),
        400: OpenApiResponse(
            description="Bad Request",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_ADOPT_400],
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_ADOPT_401],
        ),
        403: OpenApiResponse(
            description="Forbidden",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_ADOPT_403],
        ),
        404: OpenApiResponse(
            description="Not Found",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_ADOPT_404],
        ),
        409: OpenApiResponse(
            description="Conflict",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_ADOPT_409],
        ),
    },
)


ANSWER_COMMENT_CREATE_SCHEMA = extend_schema(
    tags=["qna"],
    summary="답변 댓글 등록 API",
    description=ApiDescriptions.ANSWER_COMMENT_CREATE,
    request=AnswerCommentCreateSerializer,
    examples=[RequestBodyExamples.ANSWER_COMMENT_CREATE],
    responses={
        201: OpenApiResponse(
            description="Created",
            response=AnswerCommentCreateResponseSerializer,
            examples=[SuccessResponseExamples.ANSWER_COMMENT_CREATE],
        ),
        400: OpenApiResponse(
            description="Bad Request",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_COMMENT_CREATE_400],
        ),
        401: OpenApiResponse(
            description="Unauthorized",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_COMMENT_CREATE_401],
        ),
        403: OpenApiResponse(
            description="Forbidden",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_COMMENT_CREATE_403],
        ),
        404: OpenApiResponse(
            description="Not Found",
            response=ErrorResponseSerializer,
            examples=[ErrorResponseExamples.ANSWER_COMMENT_CREATE_404],
        ),
    },
)
