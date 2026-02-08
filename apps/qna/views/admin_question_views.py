from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.serializers.admin.question.response import (
    AdminQuestionDeleteResponseSerializer,
)
from apps.qna.services.admin.question.command import AdminQuestionCommandService
from apps.qna.utils.permissions import IsAdminOrStaff
from apps.qna.views.base_view import QnaBaseAPIView


class AdminQuestionDeleteAPIView(QnaBaseAPIView):
    """
    어드민 질의응답 삭제 API View
    """

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), IsAdminOrStaff()]

    @extend_schema(
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
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_QUESTION_DELETE_400],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_QUESTION_DELETE_401],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_QUESTION_DELETE_403],
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_QUESTION_DELETE_404],
            ),
        },
    )
    def delete(self, request: Request, question_id: int) -> Response:
        """어드민 질의응답 삭제"""
        delete_summary = AdminQuestionCommandService.delete_question(question_id=question_id)

        response_serializer = AdminQuestionDeleteResponseSerializer(delete_summary)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
