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
from apps.exams.schemas.admin import admin_exam_deployment_status_schema
from apps.exams.serializers.admin.deployments_status import (
    AdminExamDeploymentStatusRequestSerializer,
    AdminExamDeploymentStatusResponseSerializer,
)
from apps.exams.services.admin.deployments_status import update_deployment_status
from apps.exams.validators import parse_positive_int
from apps.exams.views.mixins import ExamsExceptionMixin


@admin_exam_deployment_status_schema
class AdminExamDeploymentStatusAPIView(ExamsExceptionMixin, APIView):
    # 어드민 배포 상태 변경
    """어드민 쪽지시험 배포 상태 변경 API."""

    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = AdminExamDeploymentStatusRequestSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=ErrorMessages.NO_DEPLOYMENT_STATUS_PERMISSION.value)

    def patch(self, request: Request, deployment_id: int) -> Response:
        parse_positive_int(deployment_id, ErrorMessages.INVALID_DEPLOYMENT_STATUS_REQUEST)
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            raise_error(ErrorMessages.INVALID_DEPLOYMENT_STATUS_REQUEST)

        deployment = update_deployment_status(deployment_id, serializer.validated_data["status"])

        response_serializer = AdminExamDeploymentStatusResponseSerializer(
            {
                "deployment_id": deployment.id,
                "status": serializer.validated_data["status"],
            }
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)
