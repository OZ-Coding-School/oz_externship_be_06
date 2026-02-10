from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStudentRole
from apps.exams.constants import ErrorMessages, ExamStatus
from apps.exams.error_map import raise_error
from apps.exams.models import ExamDeployment
from apps.exams.schemas.student import exam_status_check_schema
from apps.exams.serializers.student.deployments_status import ExamStatusResponseSerializer
from apps.exams.services.student.auto_submit import auto_submit_if_overdue
from apps.exams.services.student.deployments_status import (
    get_deployment_or_404,
    get_exam_status,
)
from apps.exams.validators import parse_positive_int
from apps.exams.views.mixins import ExamsExceptionMixin


# 시험 상태 확인
@exam_status_check_schema
class ExamStatusCheckAPIView(ExamsExceptionMixin, APIView):
    """수강생 응시 세션의 현재 시험 상태를 조회."""

    permission_classes = [IsAuthenticated, IsStudentRole]
    serializer_class = ExamStatusResponseSerializer

    def get(self, request: Request, deployment_id: int) -> Response:
        parse_positive_int(deployment_id, ErrorMessages.EXAM_NOT_FOUND)
        deployment = get_deployment_or_404(deployment_id, error_message=ErrorMessages.EXAM_NOT_FOUND)

        user_id = request.user.id
        if user_id is None:
            raise_error(ErrorMessages.UNAUTHORIZED)

        force_by_admin = deployment.status != ExamDeployment.StatusChoices.ACTIVATED
        auto_submitted = auto_submit_if_overdue(deployment=deployment, user_id=user_id, force=force_by_admin).submitted
        exam_status = ExamStatus.CLOSED if auto_submitted else get_exam_status(deployment)
        is_closed = exam_status == ExamStatus.CLOSED
        serializer = self.serializer_class(
            data={
                "exam_status": exam_status.value,
                "force_submit": is_closed,
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
