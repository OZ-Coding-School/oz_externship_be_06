from typing import Any

from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.utils.permissions import CanWriteAnswerComment
from apps.qna.docs.schemas_answer import (
    AI_ANSWER_GENERATE_SCHEMA,
    ANSWER_ADOPT_SCHEMA,
    ANSWER_COMMENT_CREATE_SCHEMA,
    ANSWER_CREATE_SCHEMA,
    ANSWER_UPDATE_SCHEMA,
)
from apps.qna.models import QuestionAIAnswer
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
from apps.qna.services.answer.command import (
    AIAnswerCommandService,
    AnswerCommandService,
    AnswerCommentCommandService,
)
from apps.qna.views.base_view import QnaBaseAPIView


class AIAnswerGenerateAPIView(QnaBaseAPIView):
    """
    /api/v1/qna/questions/{question_id}/ai-answer
    [GET] 질문에 대한 AI 답변 생성 및 결과 반환
    """

    # 사용할 AI 모델 설정 (Gemini 또는 GPT)
    # - QuestionAIAnswer.AIModel.GEMINI: gemini-2.5-pro 모델 사용 (기본값)
    # - QuestionAIAnswer.AIModel.GPT: (미구현)
    using_model: str = QuestionAIAnswer.AIModel.GEMINI

    serializer_classes = {"GET": None}

    def get_permissions(self) -> list[Any]:
        method = self.request.method or ""
        if method == "GET":
            return [IsAuthenticated()]
        raise MethodNotAllowed(method)

    # [GET] AI 생성 답변 조회
    @AI_ANSWER_GENERATE_SCHEMA
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


class AnswerCreateAPIView(QnaBaseAPIView):
    """
    /api/v1/qna/questions/{question_id}/answers
    [POST] 질문에 대한 답변 등록
    """

    serializer_classes = {"POST": AnswerCreateSerializer}

    def get_permissions(self) -> list[Any]:
        method = self.request.method or ""
        if method == "POST":
            return [IsAuthenticated(), CanWriteAnswerComment()]
        raise MethodNotAllowed(method)

    # [POST] 답변 등록
    @ANSWER_CREATE_SCHEMA
    def post(self, request: Request, question_id: int) -> Response:
        """답변 생성"""
        serializer = AnswerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 서비스 호출
        answer = AnswerCommandService.create_answer(
            question_id=question_id, author=self.request_user, data=serializer.validated_data
        )

        # 응답 출력
        response_serializer = AnswerCreateResponseSerializer(answer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class AnswerUpdateAPIView(QnaBaseAPIView):
    """
    /api/v1/qna/answers/{answer_id}
    [PUT] 답변 수정
    """

    serializer_classes = {"PUT": AnswerUpdateSerializer}

    def get_permissions(self) -> list[Any]:
        method = self.request.method or ""
        if method == "PUT":
            return [IsAuthenticated(), CanWriteAnswerComment()]
        raise MethodNotAllowed(method)

    # [PUT] 답변 수정
    @ANSWER_UPDATE_SCHEMA
    def put(self, request: Request, answer_id: int) -> Response:
        """답변 수정"""
        serializer = AnswerUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 서비스 호출
        answer = AnswerCommandService.update_answer(
            answer_id=answer_id, user=self.request_user, data=serializer.validated_data
        )

        # 응답 출력
        response_serializer = AnswerUpdateResponseSerializer(answer)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class AnswerAdoptAPIView(QnaBaseAPIView):
    """
    /api/v1/qna/answers/{answer_id}/accept
    [POST] 답변 채택
    """

    serializer_classes = {"POST": None}

    def get_permissions(self) -> list[Any]:
        method = self.request.method or ""
        if method == "POST":
            return [IsAuthenticated()]
        raise MethodNotAllowed(method)

    # [POST] 답변 채택
    @ANSWER_ADOPT_SCHEMA
    def post(self, request: Request, answer_id: int) -> Response:
        """답변 채택 처리"""
        # 서비스 호출
        answer = AnswerCommandService.adopt_answer(answer_id=answer_id, user=self.request_user)

        # 응답 출력
        response_serializer = AnswerAdoptResponseSerializer(answer)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class AnswerCommentCreateAPIView(QnaBaseAPIView):
    """
    /api/v1/qna/answers/{answer_id}/comments
    [POST] 답변에 대한 댓글 등록
    """

    serializer_classes = {"POST": AnswerCommentCreateSerializer}

    def get_permissions(self) -> list[Any]:
        method = self.request.method or ""
        if method == "POST":
            return [IsAuthenticated(), CanWriteAnswerComment()]
        raise MethodNotAllowed(method)

    # [POST] 댓글 등록
    @ANSWER_COMMENT_CREATE_SCHEMA
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
