from __future__ import annotations

from typing import NoReturn

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.serializers.admin.exams_create import (
    AdminExamCreateRequestSerializer,
    AdminExamCreateResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin.exams_create import (
    ExamCreateConflictError,
    ExamCreateNotFoundError,
    create_exam,
)
from apps.exams.views.mixins import ExamsExceptionMixin


@extend_schema(
    tags=["admin_exams"],
    summary="어드민 시험 생성",
    description="관리자/스태프 권한으로 쪽지시험을 생성합니다.",
    request=AdminExamCreateRequestSerializer,
    responses={
        201: AdminExamCreateResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 시험 생성 요청",
                    value={"error_detail": ErrorMessages.INVALID_EXAM_CREATE_REQUEST.value},
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                )
            ],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": ErrorMessages.NO_EXAM_CREATE_PERMISSION.value},
                )
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "과목 정보 없음",
                    value={"error_detail": ErrorMessages.SUBJECT_NOT_FOUND.value},
                )
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "시험 이름 중복",
                    value={"error_detail": ErrorMessages.EXAM_CONFLICT.value},
                )
            ],
        ),
    },
)
class AdminExamCreateAPIView(ExamsExceptionMixin, APIView):
    """관리자 쪽지시험 생성 API."""

    permission_classes = [IsAuthenticated, IsStaffRole]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = AdminExamCreateRequestSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=ErrorMessages.NO_EXAM_CREATE_PERMISSION.value)

    def post(self, request: Request) -> Response:
        serializer = AdminExamCreateRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": ErrorMessages.INVALID_EXAM_CREATE_REQUEST.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        try:
            exam = create_exam(
                title=data["title"],
                subject_id=data["subject_id"],
                thumbnail_img=data["thumbnail_img"],
            )
        except ExamCreateNotFoundError:
            return Response(
                {"error_detail": ErrorMessages.SUBJECT_NOT_FOUND.value},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ExamCreateConflictError:
            return Response(
                {"error_detail": ErrorMessages.EXAM_CONFLICT.value},
                status=status.HTTP_409_CONFLICT,
            )

        response_serializer = AdminExamCreateResponseSerializer(exam)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
