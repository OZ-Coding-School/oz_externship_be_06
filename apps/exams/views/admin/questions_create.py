from typing import NoReturn

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers.error import ErrorResponseSerializer
from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.serializers.admin.questions_create import (
    AdminExamQuestionCreateRequestSerializer,
    AdminExamQuestionCreateResponseSerializer,
)
from apps.exams.services.admin.questions_create import create_exam_question
from apps.exams.validators import parse_positive_int
from apps.exams.views.mixins import ExamsExceptionMixin


@extend_schema(
    tags=["admin_exams"],
    summary="어드민 문제 등록",
    description="쪽지시험 문제를 등록합니다.",
    request=AdminExamQuestionCreateRequestSerializer,
    responses={
        201: AdminExamQuestionCreateResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 문제 등록 요청",
                    value={"error_detail": ErrorMessages.INVALID_QUESTION_CREATE_REQUEST.value},
                ),
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                ),
            ],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": ErrorMessages.NO_QUESTION_CREATE_PERMISSION.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "시험 정보 없음",
                    value={"error_detail": ErrorMessages.EXAM_ADMIN_NOT_FOUND.value},
                ),
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "문제 등록 제한 초과",
                    value={"error_detail": ErrorMessages.QUESTION_CREATE_CONFLICT.value},
                ),
            ],
        ),
    },
)
class AdminExamQuestionCreateAPIView(ExamsExceptionMixin, APIView):
    """어드민 쪽지시험 문제 등록 API."""

    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = AdminExamQuestionCreateRequestSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=ErrorMessages.NO_QUESTION_CREATE_PERMISSION.value)

    def post(self, request: Request, exam_id: int) -> Response:
        parse_positive_int(exam_id, ErrorMessages.INVALID_QUESTION_CREATE_REQUEST)
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            raise_error(ErrorMessages.INVALID_QUESTION_CREATE_REQUEST)

        result = create_exam_question(exam_id, serializer.validated_data)

        return Response(AdminExamQuestionCreateResponseSerializer(result).data, status=status.HTTP_201_CREATED)
