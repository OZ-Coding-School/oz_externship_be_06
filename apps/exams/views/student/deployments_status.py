from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStudentRole
from apps.exams.constants import ErrorMessages, ExamStatus
from apps.exams.models import ExamDeployment
from apps.exams.serializers.student.deployments_status import (
    ExamStatusResponseSerializer,
)
from apps.exams.services.student.deployments_status import get_exam_status
from apps.exams.views.mixins import ExamsExceptionMixin


class ExamStatusCheckAPIView(ExamsExceptionMixin, APIView):
    """수강생 응시 세션의 현재 시험 상태를 조회."""

    permission_classes = [IsAuthenticated, IsStudentRole]
    serializer_class = ExamStatusResponseSerializer

    def get(self, request: Request, deployment_id: int) -> Response:
        try:
            deployment = ExamDeployment.objects.select_related("exam", "cohort").get(id=deployment_id)
        except ExamDeployment.DoesNotExist:
            return Response(
                {"error_detail": ErrorMessages.EXAM_NOT_FOUND.value},
                status=status.HTTP_404_NOT_FOUND,
            )

        exam_status = get_exam_status(deployment)
        is_closed = exam_status == ExamStatus.CLOSED
        serializer = self.serializer_class(
            data={
                "exam_status": exam_status.value,
                "force_submit": is_closed,
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
