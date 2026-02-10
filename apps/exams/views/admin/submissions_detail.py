from typing import NoReturn

from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.schemas.admin import (
    admin_exam_submission_delete_schema,
    admin_exam_submission_detail_schema,
)
from apps.exams.serializers.admin.submissions_delete import (
    AdminExamSubmissionDeleteResponseSerializer,
)
from apps.exams.serializers.admin.submissions_detail import (
    AdminExamSubmissionDetailResponseSerializer,
)
from apps.exams.services.admin.submissions_delete import delete_exam_submission
from apps.exams.services.admin.submissions_detail import get_admin_submission_detail
from apps.exams.validators import parse_positive_int
from apps.exams.views.mixins import ExamsExceptionMixin


# 어드민 응시 내역 상세 조회/삭제
class AdminExamSubmissionDetailAPIView(ExamsExceptionMixin, APIView):
    """어드민 쪽지시험 응시 내역 상세 조회/삭제 API."""

    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = AdminExamSubmissionDetailResponseSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        detail_message = (
            ErrorMessages.NO_SUBMISSION_DELETE_PERMISSION.value
            if request.method == "DELETE"
            else ErrorMessages.NO_SUBMISSION_DETAIL_PERMISSION.value
        )
        raise PermissionDenied(detail=detail_message)

    @admin_exam_submission_detail_schema
    def get(self, request: Request, submission_id: int) -> Response:
        parse_positive_int(submission_id, ErrorMessages.INVALID_SUBMISSION_DETAIL_REQUEST)

        payload = get_admin_submission_detail(submission_id)
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @admin_exam_submission_delete_schema
    def delete(self, request: Request, submission_id: int) -> Response:
        parse_positive_int(submission_id, ErrorMessages.INVALID_SUBMISSION_DELETE_REQUEST)

        result = delete_exam_submission(submission_id)
        serializer = AdminExamSubmissionDeleteResponseSerializer(data=result)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
