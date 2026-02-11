from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.utils.permissions import IsStaffRole
from apps.qna.docs.schemas_admin_question import ADMIN_QUESTION_DETAIL_SCHEMA
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
    @ADMIN_QUESTION_DETAIL_SCHEMA
    def get(self, request: Request, question_id: int) -> Response:
        question = AdminQuestionQueryService.get_question_detail(question_id)

        response_serializer = AdminQuestionDetailResponseSerializer(cast(Any, question))
        return Response(response_serializer.data, status=status.HTTP_200_OK)
