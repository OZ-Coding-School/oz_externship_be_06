from typing import NoReturn

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.views.mixins import ExamsExceptionMixin

from apps.exams.constants import ErrorMessages
from apps.exams.permissions import IsExamStaff
from apps.exams.serializers.admin.deployments_create import (
    AdminExamDeploymentCreateRequestSerializer,
    AdminExamDeploymentCreateResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin.deployments_create import (
    ExamDeploymentConflictError,
    ExamDeploymentNotFoundError,
    create_exam_deployment,
)


class AdminExamDeploymentCreateAPIView(ExamsExceptionMixin, APIView):
    """어드민 쪽지시험 배포 생성 API."""

    permission_classes = [IsAuthenticated, IsExamStaff]
    serializer_class = AdminExamDeploymentCreateRequestSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail=ErrorMessages.UNAUTHORIZED.value)
        raise PermissionDenied(detail=ErrorMessages.NO_DEPLOYMENT_CREATE_PERMISSION.value)

    @extend_schema(
        tags=["admin_exams"],
        summary="어드민 쪽지시험 배포 생성 API",
        description="""
        스태프/관리자가 쪽지시험 배포를 생성합니다.
        배포 생성 시 문제 스냅샷과 참가 코드가 생성됩니다.
        """,
        request=AdminExamDeploymentCreateRequestSerializer,
        responses={
            201: AdminExamDeploymentCreateResponseSerializer,
            400: OpenApiResponse(
                ErrorResponseSerializer, description=ErrorMessages.INVALID_DEPLOYMENT_CREATE_REQUEST.value
            ),
            401: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.UNAUTHORIZED.value),
            403: OpenApiResponse(
                ErrorResponseSerializer, description=ErrorMessages.NO_DEPLOYMENT_CREATE_PERMISSION.value
            ),
            404: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.DEPLOYMENT_TARGET_NOT_FOUND.value),
            409: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.DUPLICATE_DEPLOYMENT.value),
        },
    )
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
