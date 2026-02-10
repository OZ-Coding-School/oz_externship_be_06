from typing import NoReturn

from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import Exam, ExamQuestion
from apps.exams.schemas.admin import (
    admin_exam_delete_schema,
    admin_exam_detail_schema,
    admin_exam_update_schema,
)
from apps.exams.serializers.admin.exams_delete import AdminExamDeleteResponseSerializer
from apps.exams.serializers.admin.exams_detail import AdminExamDetailSerializer
from apps.exams.serializers.admin.exams_update import (
    AdminExamUpdateRequestSerializer,
    AdminExamUpdateResponseSerializer,
)
from apps.exams.services.admin.exams_delete import delete_exam
from apps.exams.services.admin.exams_detail import get_exam_detail_or_error
from apps.exams.services.admin.exams_update import update_exam
from apps.exams.validators import parse_positive_int
from apps.exams.views.mixins import ExamsExceptionMixin


# 어드민 시험 상세 조회/수정/삭제
class AdminExamDetailAPIView(ExamsExceptionMixin, APIView):
    """단일 Exam 리소스 조회/수정/삭제 API (단일 URL + HTTP 메소드 분리)"""

    permission_classes = [IsAuthenticated, IsStaffRole]

    # 401/403
    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail=ErrorMessages.UNAUTHORIZED.value)

        if request.method == "PUT":
            raise PermissionDenied(detail=ErrorMessages.NO_EXAM_UPDATE_PERMISSION.value)
        elif request.method == "DELETE":
            raise PermissionDenied(detail=ErrorMessages.NO_EXAM_DELETE_PERMISSION.value)
        elif request.method == "GET":
            raise PermissionDenied(detail=ErrorMessages.NO_EXAM_LIST_PERMISSION.value)
        else:
            raise PermissionDenied()

    @admin_exam_detail_schema
    def get(self, request: Request, exam_id: int) -> Response:
        parse_positive_int(exam_id, ErrorMessages.INVALID_EXAM_LIST_REQUEST)
        exam = get_exam_detail_or_error(exam_id=exam_id)
        serializer = AdminExamDetailSerializer(exam)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PUT → 수정
    @admin_exam_update_schema
    def put(self, request: Request, exam_id: int) -> Response:
        parse_positive_int(exam_id, ErrorMessages.INVALID_EXAM_UPDATE_REQUEST)
        serializer = AdminExamUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            raise_error(ErrorMessages.INVALID_EXAM_UPDATE_REQUEST)

        exam = update_exam(
            exam_id=exam_id,
            **serializer.validated_data,
        )

        response_serializer = AdminExamUpdateResponseSerializer(exam)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # DELETE → 삭제
    @admin_exam_delete_schema
    def delete(self, request: Request, exam_id: int) -> Response:
        parse_positive_int(exam_id, ErrorMessages.INVALID_EXAM_DELETE_REQUEST)

        deleted_id = delete_exam(exam_id)

        serializer = AdminExamDeleteResponseSerializer({"id": deleted_id})
        return Response(serializer.data, status=status.HTTP_200_OK)
