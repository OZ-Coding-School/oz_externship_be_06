from typing import Any, cast

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_request_examples import (
    QueryParameterExamples,
    RequestBodyExamples,
)
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.models import QuestionAIAnswer
from apps.qna.serializers.answer.request import (
    AnswerCommentCreateSerializer,
    AnswerCreateSerializer,
)
from apps.qna.serializers.answer.response import (
    AIAnswerResponseSerializer,
    AnswerAdoptResponseSerializer,
    AnswerCommentCreateResponseSerializer,
    AnswerCreateResponseSerializer,
)
from apps.qna.services.answer.command import (
    AIAnswerCommandService,
    AnswerCommandService,
    AnswerCommentCommandService,
)
from apps.qna.utils.model_types import User
from apps.qna.utils.permissions import CanWriteAnswer, CanWriteComment
from apps.qna.views.base_view import QnaBaseAPIView


class AnswerCreateAPIView(QnaBaseAPIView):
    """
    질문에 대한 답변 등록 API View
    """

    permission_classes = [IsAuthenticated, CanWriteComment]
    serializer_class = AnswerCreateSerializer

    # 답변 등록
    # [POST] /api/v1/qna/questions/{question_id}/answers
    @extend_schema(
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
                response=dict,
                examples=[ErrorResponseExamples.ANSWER_CREATE_400],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=[ErrorResponseExamples.ANSWER_CREATE_401],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=[ErrorResponseExamples.ANSWER_CREATE_403],
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=[ErrorResponseExamples.ANSWER_CREATE_404],
            ),
        },
        tags=["qna"],
    )
    def post(self, request: Request, question_id: int) -> Response:
        """답변 생성"""
        # Request serializer
        request_serializer = AnswerCreateSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        validated_data = request_serializer.validated_data

        # Service (command)
        answer = AnswerCommandService.create_answer(
            question_id=question_id, author=cast(User, request.user), data=validated_data
        )

        # Response serializer & Response
        response_serializer = AnswerCreateResponseSerializer(answer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class AnswerAdoptAPIView(QnaBaseAPIView):
    """
    답변 채택 API View
    """

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated()]

    # 답변 채택
    # [POST] /api/v1/qna/answers/{answer_id}/accept
    @extend_schema(
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
                response=dict,
                examples=[ErrorResponseExamples.ANSWER_ADOPT_400],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=[ErrorResponseExamples.ANSWER_ADOPT_401],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=[ErrorResponseExamples.ANSWER_ADOPT_403],
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=[ErrorResponseExamples.ANSWER_ADOPT_404],
            ),
            409: OpenApiResponse(
                description="Conflict",
                response=dict,
                examples=[ErrorResponseExamples.ANSWER_ADOPT_409],
            ),
        },
    )
    def post(self, request: Request, answer_id: int) -> Response:
        """답변 채택 처리"""
        # 서비스 호출
        answer = AnswerCommandService.adopt_answer(answer_id=answer_id, user=cast(User, request.user))

        # 응답 출력
        response_serializer = AnswerAdoptResponseSerializer(answer)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class AnswerCommentCreateAPIView(QnaBaseAPIView):
    """
    답변에 대한 댓글 등록 API View
    """

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), CanWriteAnswer()]

    # 댓글 등록
    # [POST] /api/v1/qna/answers/{answer_id}/comments
    @extend_schema(
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
                response=dict,
                examples=[ErrorResponseExamples.ANSWER_COMMENT_CREATE_400],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=[ErrorResponseExamples.ANSWER_COMMENT_CREATE_401],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=[ErrorResponseExamples.ANSWER_COMMENT_CREATE_403],
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=[ErrorResponseExamples.ANSWER_COMMENT_CREATE_404],
            ),
        },
    )
    def post(self, request: Request, answer_id: int) -> Response:
        """댓글 생성"""
        serializer = AnswerCommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = AnswerCommentCommandService.create_comment(
            answer_id=answer_id,
            author=self.request_user,
            content=serializer.validated_data["content"],
        )

        response_serializer = AnswerCommentCreateResponseSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class AIAnswerGenerateAPIView(QnaBaseAPIView):
    """
    질문에 대한 AI 답변 생성 및 결과 반환 API
    """

    # 사용할 AI 모델 설정 (Gemini 또는 GPT)
    """
    사용할 AI 모델을 설정합니다.
    - QuestionAIAnswer.AIModel.GEMINI: gemini-2.5-pro 모델 사용 (기본값)
    - QuestionAIAnswer.AIModel.GPT: gpt-4o 모델 사용
    """
    using_model: str = QuestionAIAnswer.AIModel.GEMINI

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated()]

    # AI 생성 답변 조회
    # [GET] /api/v1/qna/questions/{question_id}/ai-answer
    @extend_schema(
        summary="AI 답변 생성 API",
        description=ApiDescriptions.AI_GEN_ANSWER,
        responses={
            201: OpenApiResponse(
                description="Created",
                response=AIAnswerResponseSerializer,
                examples=[SuccessResponseExamples.AI_GEN_ANSWER],
            ),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=[ErrorResponseExamples.AI_GEN_ANSWER_400],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=[ErrorResponseExamples.AI_GEN_ANSWER_401],
            ),
            # 현재는 401 로그인 권한까지만 검증하도록 구현되어 403에러는 발생하지 않음
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=[ErrorResponseExamples.AI_GEN_ANSWER_403],
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=[ErrorResponseExamples.AI_GEN_ANSWER_404],
            ),
            409: OpenApiResponse(
                description="Conflict",
                response=dict,
                examples=[ErrorResponseExamples.AI_GEN_ANSWER_409],
            ),
        },
        tags=["qna"],
    )
    def get(self, request: Request, question_id: int) -> Response:
        """질문 ID를 받아 AI 답변을 생성하고 저장된 결과를 반환함"""
        # 서비스 레이어 호출 (비즈니스 로직 및 예외 처리 집중)
        ai_answer = AIAnswerCommandService.generate_ai_answer(
            question_id=question_id,
            using_model=self.using_model,
        )

        # 응답 변환
        serializer = AIAnswerResponseSerializer(ai_answer)

        # 명세서에 201이 명시되어 있으므로 Created 상태 코드로 반환
        return Response(serializer.data, status=status.HTTP_201_CREATED)
