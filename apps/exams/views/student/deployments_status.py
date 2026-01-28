from typing import NoReturn

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ErrorMessages, ExamStatus
from apps.exams.models import ExamDeployment
from apps.exams.permissions import IsStudentRole
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.serializers.student.deployments_status import (
    ExamStatusResponseSerializer,
)
from apps.exams.services.student.deployments_status import is_exam_active


class ExamStatusCheckAPIView(APIView):
    """수강생 응시 세션의 현재 시험 상태를 조회."""

    permission_classes = [IsAuthenticated, IsStudentRole]
    serializer_class = ExamStatusResponseSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail=ErrorMessages.UNAUTHORIZED.value)
        raise PermissionDenied(detail=ErrorMessages.FORBIDDEN.value)

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 상태 확인 API",
        description="""
        수강생이 쪽지시험 응시 중인 상태를 확인합니다.
        시험이 종료되었거나 비활성화된 경우 force_submit=True로 응답합니다.
        """,
        parameters=[
            OpenApiParameter(
                name="deployment_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description="시험 배포 ID",
            )
        ],
        responses={
            200: ExamStatusResponseSerializer,
            401: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.UNAUTHORIZED.value),
            403: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.FORBIDDEN.value),
            404: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.EXAM_NOT_FOUND.value),
        },
    )
    def get(self, request: Request, deployment_id: int) -> Response:
        try:
            deployment = ExamDeployment.objects.select_related("exam", "cohort").get(id=deployment_id)
        except ExamDeployment.DoesNotExist:
            return Response(
                {"error_detail": ErrorMessages.EXAM_NOT_FOUND.value},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_closed = not is_exam_active(deployment)
        serializer = self.serializer_class(
            data={
                "exam_status": (ExamStatus.CLOSED if is_closed else ExamStatus.ACTIVATED).value,
                "force_submit": is_closed,
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
