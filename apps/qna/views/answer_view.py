from typing import cast

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

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
        description="""
        ### 수강생, 조교, 코치, 매니저, 관리자 역할의 로그인 유저가 질문에 대한 답변을 등록합니다.
        - 답변 작성 시 입력 항목
            - 답변 내용 ( 마크다운 형식으로 작성 가능, 이미지 파일 첨부 가능)
        """,
        request=ser_ans_reqs.AnswerCreateSerializer,
        responses={
            201: OpenApiResponse(response=ser_ans_rep.AnswerCreateResponseSerializer, description="답변 등록 성공"),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=[
                    OpenApiExample(
                        name="잘못된 요청 예시",
                        value={"error_detail": "유효하지 않은 답변 등록 요청입니다."},
                        description="잘못된 요청 예시",
                    ),
                ],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=[
                    OpenApiExample(
                        name="인증 실패 예시",
                        value={"error_detail": "로그인한 사용자만 답변을 작성할 수 있습니다."},
                        description="인증 실패 예시",
                    ),
                ],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=[
                    OpenApiExample(
                        name="권한 없음 예시",
                        value={"error_detail": "답변 작성 권한이 없습니다."},
                        description="권한 없음 예시",
                    ),
                ],
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=[
                    OpenApiExample(
                        name="질문 없음 예시",
                        value={"error_detail": "해당 질문을 찾을 수 없습니다."},
                        description="질문 없음 예시",
                    ),
                ],
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
