from typing import NoReturn

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ErrorMessages
from apps.exams.permissions import IsExamStaff
from apps.exams.serializers.admin.deployments_status import (
    AdminExamDeploymentStatusRequestSerializer,
    AdminExamDeploymentStatusResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin.deployments_status import (
    ExamDeploymentStatusConflictError,
    ExamDeploymentStatusNotFoundError,
    update_deployment_status,
)


class AdminExamDeploymentStatusAPIView(APIView):
    """어드민 쪽지시험 배포 상태 변경 API."""

    permission_classes = [IsAuthenticated, IsExamStaff]
    serializer_class = AdminExamDeploymentStatusRequestSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail=ErrorMessages.UNAUTHORIZED.value)
        raise PermissionDenied(detail=ErrorMessages.NO_DEPLOYMENT_STATUS_PERMISSION.value)

    @extend_schema(
        tags=["admin_exams"],
        summary="어드민 쪽지시험 배포 상태 변경 API",
        description="""
        스태프/관리자가 쪽지시험 배포를 활성화/비활성화합니다.
        """,
        request=AdminExamDeploymentStatusRequestSerializer,
        responses={
            200: AdminExamDeploymentStatusResponseSerializer,
            400: OpenApiResponse(
                ErrorResponseSerializer, description=ErrorMessages.INVALID_DEPLOYMENT_STATUS_REQUEST.value
            ),
            401: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.UNAUTHORIZED.value),
            403: OpenApiResponse(
                ErrorResponseSerializer, description=ErrorMessages.NO_DEPLOYMENT_STATUS_PERMISSION.value
            ),
            404: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.DEPLOYMENT_NOT_FOUND.value),
            409: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.DEPLOYMENT_CONFLICT.value),
        },
    )
    def patch(self, request: Request, deployment_id: int) -> Response:
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": ErrorMessages.INVALID_DEPLOYMENT_STATUS_REQUEST.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            deployment = update_deployment_status(deployment_id, serializer.validated_data["status"])
        except ExamDeploymentStatusNotFoundError:
            return Response(
                {"error_detail": ErrorMessages.DEPLOYMENT_NOT_FOUND.value},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ExamDeploymentStatusConflictError:
            return Response(
                {"error_detail": ErrorMessages.DEPLOYMENT_CONFLICT.value},
                status=status.HTTP_409_CONFLICT,
            )

        response_serializer = AdminExamDeploymentStatusResponseSerializer(
            {
                "deployment_id": deployment.id,
                "status": serializer.validated_data["status"],
            }
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)
