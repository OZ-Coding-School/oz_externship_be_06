from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.serializers.admin.question.request import AdminQuestionListQuerySerializer
from apps.qna.serializers.admin.question.response import (
    AdminQuestionListResponseSerializer,
)
from apps.qna.services.admin.question.query import AdminQuestionQueryService
from apps.qna.utils.permissions import IsAdminOrStaff
from apps.qna.utils.qna_paginator import AdminQuestionListPaginator as Paginator
from apps.qna.views.base_view import QnaBaseAPIView


class AdminQuestionListAPIView(QnaBaseAPIView):
    """
    어드민 질의응답 목록 조회 API View
    """

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), IsAdminOrStaff()]

    serializer_class = AdminQuestionListQuerySerializer

    @extend_schema(
        tags=["admin_qna"],
        summary="어드민 질의응답 목록 조회 API",
        description=ApiDescriptions.ADMIN_QUESTION_LIST,
        parameters=[AdminQuestionListQuerySerializer],
        responses={
            200: OpenApiResponse(
                description="OK",
                response=AdminQuestionListResponseSerializer,
                examples=[SuccessResponseExamples.ADMIN_QUESTION_LIST],
            ),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_QUESTION_LIST_400],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_QUESTION_LIST_401],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=[ErrorResponseExamples.ADMIN_QUESTION_LIST_403],
            ),
        },
    )
    def get(self, request: Request) -> Response:
        """어드민 질의응답 목록 조회"""
        # Request serializer
        request_serializer = AdminQuestionListQuerySerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)
        validated_data = request_serializer.validated_data

        # Service (query)
        question_list = AdminQuestionQueryService.get_question_list(filters=validated_data)

        # Response serializer & Paginated response
        return Paginator.get_paginated_data_response(
            queryset=question_list, request=request, serializer_class=AdminQuestionListResponseSerializer, view=self
        )
