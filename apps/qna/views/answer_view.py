from typing import cast

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
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
from apps.qna.serializers.answer import request as ser_ans_reqs
from apps.qna.serializers.answer import response as ser_ans_rep
from apps.qna.services.answer import command as svc_ans_cmd
from apps.qna.utils.model_types import User
from apps.qna.utils.permissions import CanWriteAnswer
from apps.qna.views.base_view import QnaBaseAPIView


class AnswerCreateAPIView(QnaBaseAPIView):
    """
    질문에 대한 답변 등록 API View
    """

    permission_classes = [IsAuthenticated, CanWriteAnswer]

    # 답변 등록
    # [POST] /api/v1/qna/questions/{question_id}/answers
    @extend_schema(
        summary="답변 등록 API",
        description=ApiDescriptions.ANSWER_CREATE,
        request=ser_ans_reqs.AnswerCreateSerializer,
        examples=RequestBodyExamples.ANSWER_CREATE,
        responses={
            201: OpenApiResponse(
                description="답변 등록 성공",
                response=ser_ans_rep.AnswerCreateResponseSerializer,
                examples=SuccessResponseExamples.ANSWER_CREATE,
            ),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=ErrorResponseExamples.ANSWER_CREATE_400,
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=ErrorResponseExamples.ANSWER_CREATE_401,
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=ErrorResponseExamples.ANSWER_CREATE_403,
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=ErrorResponseExamples.ANSWER_CREATE_404,
            ),
        },
        tags=["qna"],
    )
    def post(self, request: Request, question_id: int) -> Response:
        """답변 생성"""
        serializer = ser_ans_reqs.AnswerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 서비스 호출
        answer = svc_ans_cmd.AnswerCommandService.create_answer(
            question_id=question_id, author=cast(User, request.user), data=serializer.validated_data
        )

        # 응답 출력
        response_serializer = ser_ans_rep.AnswerCreateResponseSerializer(answer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
