from __future__ import annotations

from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.utils.permissions import IsStaffRole
from apps.qna.docs.schemas_admin_question import (
    ADMIN_QUESTION_DELETE_SCHEMA,
    ADMIN_QUESTION_DETAIL_SCHEMA,
    ADMIN_QUESTION_LIST_SCHEMA,
)
from apps.qna.serializers.admin.question.request import (
    AdminQuestionListQuerySerializer,
)
from apps.qna.serializers.admin.question.response import (
    AdminQuestionDeleteResponseSerializer,
    AdminQuestionDetailResponseSerializer,
    AdminQuestionListResponseSerializer,
)
from apps.qna.services.admin.question.command import AdminQuestionCommandService
from apps.qna.services.admin.question.query import AdminQuestionQueryService
from apps.qna.utils.qna_paginator import AdminQuestionListPaginator as Paginator
from apps.qna.views.base_view import QnaBaseAPIView


class AdminQuestionListAPIView(QnaBaseAPIView):
    """
    /api/v1/admin/qna/questions
    [GET] 어드민 질의응답 목록 조회
    """

    serializer_classes = {
        "GET": AdminQuestionListQuerySerializer,
    }

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), IsStaffRole()]

    # [GET] 어드민 질의응답 목록 조회
    @ADMIN_QUESTION_LIST_SCHEMA
    def get(self, request: Request) -> Response:
        request_serializer = AdminQuestionListQuerySerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        question_list = AdminQuestionQueryService.get_question_list(filters=request_serializer.validated_data)

        return Paginator.get_paginated_data_response(
            queryset=question_list, request=request, serializer_class=AdminQuestionListResponseSerializer, view=self
        )


class AdminQuestionDetailAPIView(QnaBaseAPIView):
    """
    /api/v1/admin/qna/questions/{question_id}
    [GET] 어드민 질의응답 상세 조회
    [DELETE] 어드민 질의응답 삭제
    """

    serializer_classes = {
        "GET": None,
        "DELETE": None,
    }

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), IsStaffRole()]

    # [GET] 어드민 질의응답 상세 조회
    @ADMIN_QUESTION_DETAIL_SCHEMA
    def get(self, request: Request, question_id: int) -> Response:
        question = AdminQuestionQueryService.get_question_detail(question_id)

        response_serializer = AdminQuestionDetailResponseSerializer(cast(Any, question))
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # [DELETE] 어드민 질의응답 삭제
    @ADMIN_QUESTION_DELETE_SCHEMA
    def delete(self, request: Request, question_id: int) -> Response:
        delete_summary = AdminQuestionCommandService.delete_question(question_id=question_id)

        response_serializer = AdminQuestionDeleteResponseSerializer(delete_summary)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
