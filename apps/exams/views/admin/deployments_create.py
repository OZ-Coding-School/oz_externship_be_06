from typing import NoReturn

from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.serializers.admin.deployments_create import (
    AdminExamDeploymentCreateRequestSerializer,
    AdminExamDeploymentCreateResponseSerializer,
)
from apps.exams.services.admin.deployments_create import (
    ExamDeploymentConflictError,
    ExamDeploymentNotFoundError,
    create_exam_deployment,
)
from apps.exams.views.mixins import ExamsExceptionMixin


class AdminExamDeploymentCreateAPIView(ExamsExceptionMixin, APIView):
    """어드민 쪽지시험 배포 생성 API."""

    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = AdminExamDeploymentCreateRequestSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=ErrorMessages.NO_DEPLOYMENT_CREATE_PERMISSION.value)

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": ErrorMessages.INVALID_DEPLOYMENT_CREATE_REQUEST.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            deployment_id = create_exam_deployment(serializer.validated_data)
        except ExamDeploymentNotFoundError:
            return Response(
                {"error_detail": ErrorMessages.DEPLOYMENT_TARGET_NOT_FOUND.value},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ExamDeploymentConflictError:
            return Response(
                {"error_detail": ErrorMessages.DUPLICATE_DEPLOYMENT.value},
                status=status.HTTP_409_CONFLICT,
            )

        response_serializer = AdminExamDeploymentCreateResponseSerializer(data={"pk": deployment_id})
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
