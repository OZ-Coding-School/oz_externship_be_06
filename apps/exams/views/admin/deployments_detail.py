from typing import NoReturn

from django.conf import settings
from django.urls import reverse
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.serializers.admin.deployments_detail import (
    AdminExamDeploymentDetailResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin.deployments_detail import (
    ExamDeploymentDetailNotFoundError,
    get_exam_deployment_detail,
)
from apps.exams.views.mixins import ExamsExceptionMixin


@extend_schema(
    tags=["admin_exams"],
    summary="어드민 배포 상세 조회",
    description="쪽지시험 배포 상세 정보를 조회합니다.",
    responses={
        200: AdminExamDeploymentDetailResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 배포 상세 조회 요청",
                    value={"error_detail": ErrorMessages.INVALID_DEPLOYMENT_DETAIL_REQUEST.value},
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
                    value={"error_detail": ErrorMessages.NO_DEPLOYMENT_DETAIL_PERMISSION.value},
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
    },
)
class AdminExamDeploymentDetailAPIView(ExamsExceptionMixin, APIView):
    """어드민 쪽지시험 배포 상세 조회 API."""

    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = AdminExamDeploymentDetailResponseSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=ErrorMessages.NO_DEPLOYMENT_DETAIL_PERMISSION.value)

    def get(self, request: Request, deployment_id: int) -> Response:
        if deployment_id <= 0:
            return Response(
                {"error_detail": ErrorMessages.INVALID_DEPLOYMENT_DETAIL_REQUEST.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if settings.USE_EXAM_MOCK:
            access_url = request.build_absolute_uri(reverse("exams:take-exam", kwargs={"deployment_id": deployment_id}))
            payload = {
                "id": deployment_id,
                "exam_access_url": access_url,
                "access_code": "A7Bd9K",
                "cohort": {
                    "id": 11,
                    "number": 11,
                    "display": "백엔드 11기",
                    "course": {
                        "id": 12,
                        "name": "백엔드",
                        "tag": "BE",
                    },
                },
                "submit_count": 58,
                "not_submitted_count": 12,
                "duration_time": 45,
                "open_at": "2025-03-02 10:00:00",
                "close_at": "2025-03-02 12:00:00",
                "created_at": "2025-03-01 14:20:33",
                "exam": {
                    "id": 101,
                    "title": "Python 기본 문법 테스트",
                    "thumbnail_img_url": "https://img.com/images/sample.png",
                },
                "subject": {
                    "id": 32,
                    "name": "Python",
                },
            }
            serializer = self.serializer_class(payload)
            return Response(serializer.data, status=status.HTTP_200_OK)

        try:
            payload = get_exam_deployment_detail(deployment_id)
        except ExamDeploymentDetailNotFoundError:
            return Response(
                {"error_detail": ErrorMessages.DEPLOYMENT_NOT_FOUND.value},
                status=status.HTTP_404_NOT_FOUND,
            )

        access_url = request.build_absolute_uri(reverse("exams:take-exam", kwargs={"deployment_id": deployment_id}))
        payload["exam_access_url"] = access_url

        serializer = self.serializer_class(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)
