from typing import NoReturn

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
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
from apps.exams.views.mixins import ExamsExceptionMixin


@extend_schema(
    tags=["admin_exams"],
    summary="어드민 배포 상태 변경",
    description="쪽지시험 배포 상태를 변경합니다.",
    request=AdminExamDeploymentStatusRequestSerializer,
    responses={
        200: AdminExamDeploymentStatusResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 배포 상태 요청",
                    value={"error_detail": ErrorMessages.INVALID_DEPLOYMENT_STATUS_REQUEST.value},
                ),
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                ),
            ],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": ErrorMessages.NO_DEPLOYMENT_STATUS_PERMISSION.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "배포 정보 없음",
                    value={"error_detail": ErrorMessages.DEPLOYMENT_NOT_FOUND.value},
                ),
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "상태 변경 충돌",
                    value={"error_detail": ErrorMessages.DEPLOYMENT_CONFLICT.value},
                ),
            ],
        ),
    },
)
class AdminExamDeploymentStatusAPIView(ExamsExceptionMixin, APIView):
    """어드민 쪽지시험 배포 상태 변경 API."""

    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = AdminExamDeploymentStatusRequestSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=ErrorMessages.NO_DEPLOYMENT_STATUS_PERMISSION.value)

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
