from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.serializers.admin.answer.response import (
    AdminAnswerDeleteResponseSerializer,
)
from apps.qna.services.admin.answer.command import AdminAnswerCommandService


class AdminAnswerDeleteAPIView(APIView):
    """
    어드민 답변 삭제 API
    """

    permission_classes = [IsAdminUser]

    @extend_schema(
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
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_ANSWER_DELETE_400],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_ANSWER_DELETE_401],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_ANSWER_DELETE_403],
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_ANSWER_DELETE_404],
            ),
        },
    )
    def delete(self, request: Request, answer_id: int) -> Response:
        """어드민 답변 삭제"""
        delete_summary = AdminAnswerCommandService.delete_answer(answer_id=answer_id)

        response_serializer = AdminAnswerDeleteResponseSerializer(delete_summary)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
