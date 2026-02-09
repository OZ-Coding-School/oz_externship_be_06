from typing import NoReturn

from django.urls import reverse
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
    admin_exam_deployment_delete_schema,
    admin_exam_deployment_detail_schema,
    admin_exam_deployment_update_schema,
)
from apps.exams.serializers.admin.deployments_delete import (
    AdminExamDeploymentDeleteResponseSerializer,
)
from apps.exams.serializers.admin.deployments_detail import (
    AdminExamDeploymentDetailResponseSerializer,
)
from apps.exams.serializers.admin.deployments_update import (
    AdminExamDeploymentUpdateRequestSerializer,
    AdminExamDeploymentUpdateResponseSerializer,
)
from apps.exams.services.admin.deployments_delete import delete_exam_deployment
from apps.exams.services.admin.deployments_detail import get_exam_deployment_detail
from apps.exams.services.admin.deployments_update import update_exam_deployment
from apps.exams.views.mixins import ExamsExceptionMixin


# 어드민 배포 상세 조회 / 어드민 배포 수정 / 쪽지시험 배포 삭제 API
@admin_exam_deployment_detail_schema
class AdminExamDeploymentDetailAPIView(ExamsExceptionMixin, APIView):
    """어드민 쪽지시험 배포 상세 조회 API."""

    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = AdminExamDeploymentDetailResponseSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()

        if request.method == "PATCH":
            detail_message = ErrorMessages.NO_DEPLOYMENT_UPDATE_PERMISSION.value
        elif request.method == "DELETE":
            detail_message = ErrorMessages.NO_DEPLOYMENT_DELETE_PERMISSION.value
        else:
            detail_message = ErrorMessages.NO_DEPLOYMENT_DETAIL_PERMISSION.value

        raise PermissionDenied(detail=detail_message)

    def get(self, request: Request, deployment_id: int) -> Response:
        if deployment_id <= 0:
            raise_error(ErrorMessages.INVALID_DEPLOYMENT_DETAIL_REQUEST)

        payload = get_exam_deployment_detail(deployment_id)

        access_url = request.build_absolute_uri(reverse("exams:take-exam", kwargs={"deployment_id": deployment_id}))
        payload["exam_access_url"] = access_url

        serializer = self.serializer_class(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @admin_exam_deployment_update_schema
    def patch(self, request: Request, deployment_id: int) -> Response:
        """배포 정보 수정 (open_at, close_at, duration_time)."""
        if deployment_id <= 0:
            raise_error(ErrorMessages.INVALID_DEPLOYMENT_UPDATE_REQUEST)

        serializer = AdminExamDeploymentUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            raise_error(ErrorMessages.INVALID_DEPLOYMENT_UPDATE_REQUEST)

        deployment = update_exam_deployment(deployment_id, serializer.validated_data)

        response_serializer = AdminExamDeploymentUpdateResponseSerializer(
            {
                "deployment_id": deployment.id,
                "duration_time": deployment.duration_time,
                "open_at": deployment.open_at,
                "close_at": deployment.close_at,
                "updated_at": deployment.updated_at,
            }
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @admin_exam_deployment_delete_schema
    def delete(self, _request: Request, deployment_id: int) -> Response:
        if deployment_id <= 0:
            raise_error(ErrorMessages.INVALID_DEPLOYMENT_DELETE_REQUEST)

        # service에서 404 / 409 처리
        result = delete_exam_deployment(deployment_id=deployment_id)

        serializer = AdminExamDeploymentDeleteResponseSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)
