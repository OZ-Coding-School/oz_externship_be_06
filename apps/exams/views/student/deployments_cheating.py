from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStudentRole
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.schemas.student import exam_cheating_update_schema
from apps.exams.serializers.student.deployments_cheating import (
    ExamCheatingRequestSerializer,
    ExamCheatingResponseSerializer,
)
from apps.exams.services.student.deployments_cheating import update_cheating_count
from apps.exams.services.student.deployments_status import get_deployment_or_404
from apps.exams.validators import parse_positive_int
from apps.exams.views.mixins import ExamsExceptionMixin


@exam_cheating_update_schema
class ExamCheatingUpdateAPIView(ExamsExceptionMixin, APIView):
    # 부정행위 횟수 갱신
    """부정행위 횟수를 증가시키고 종료 여부를 판단."""

    permission_classes = [IsAuthenticated, IsStudentRole]
    serializer_class = ExamCheatingResponseSerializer

    def post(self, request: Request, deployment_id: int) -> Response:
        parse_positive_int(deployment_id, ErrorMessages.EXAM_NOT_FOUND)
        user = request.user

        deployment = get_deployment_or_404(deployment_id, error_message=ErrorMessages.EXAM_NOT_FOUND)

        request_serializer = ExamCheatingRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        user_id = user.id
        if user_id is None:
            raise_error(ErrorMessages.UNAUTHORIZED)

        result = update_cheating_count(
            deployment=deployment,
            user_id=user_id,
            answers_json=request_serializer.validated_data.get("answers_json", []),
        )

        serializer = self.serializer_class(
            data={
                "cheating_count": result.cheating_count,
                "exam_status": result.exam_status,
                "force_submit": result.force_submit,
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
