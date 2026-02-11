from typing import Any

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.utils.permissions import IsStaffRole
from apps.qna.docs.schemas_admin_answer import ADMIN_ANSWER_DELETE_SCHEMA
from apps.qna.serializers.admin.answer.response import (
    AdminAnswerDeleteResponseSerializer,
)
from apps.qna.services.admin.answer.command import AdminAnswerCommandService
from apps.qna.views.base_view import QnaBaseAPIView


class AdminAnswerDeleteAPIView(QnaBaseAPIView):
    """
    /api/v1/admin/qna/answers/{answer_id}
    [DELETE] 어드민 답변 삭제
    """

    serializer_classes = {"DELETE": None}

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), IsStaffRole()]

    # [DELETE] 어드민 답변 삭제
    @ADMIN_ANSWER_DELETE_SCHEMA
    def delete(self, request: Request, answer_id: int) -> Response:
        delete_summary = AdminAnswerCommandService.delete_answer(answer_id=answer_id)

        response_serializer = AdminAnswerDeleteResponseSerializer(delete_summary)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
