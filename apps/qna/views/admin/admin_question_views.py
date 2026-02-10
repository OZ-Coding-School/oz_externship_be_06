from typing import Any, cast

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.utils.permissions import IsStaffRole
from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.serializers.admin.question.response import (
    AdminQuestionDetailResponseSerializer,
)
from apps.qna.services.admin.question.query import AdminQuestionQueryService
from apps.qna.views.base_view import QnaBaseAPIView


class AdminQuestionDetailAPIView(QnaBaseAPIView):
    """
    어드민 질문 상세 조회 API View
    """

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), IsStaffRole()]

    # 어드민 질의응답 상세 조회
    # [GET] /api/v1/admin/qna/questions/{question_id}
    @extend_schema(
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
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_QUESTION_DETAIL_400],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_QUESTION_DETAIL_401],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_QUESTION_DETAIL_403],
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_QUESTION_DETAIL_404],
            ),
        },
    )
    def get(self, request: Request, question_id: int) -> Response:
        question = AdminQuestionQueryService.get_question_detail(question_id)

        serializer = AdminQuestionDetailResponseSerializer(cast(Any, question))

        return Response(serializer.data, status=status.HTTP_200_OK)
