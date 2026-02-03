from __future__ import annotations

from django.db.models import QuerySet
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.core.utils.pagination import SimplePagePagination
from apps.core.utils.permissions import IsStudentRole
from apps.exams.constants import ErrorMessages
from apps.exams.models.exam_deployments import ExamDeployment
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.serializers.student.deployments_list import (
    ExamDeploymentListSerializer,
)
from apps.exams.services.student.deployments_list import ExamDeploymentListService
from apps.exams.views.mixins import ExamsExceptionMixin


@extend_schema(
    tags=["exams"],
    summary="시험 배포 목록 조회",
    description="현재 로그인한 사용자의 코호트 기준으로 시험 목록을 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="status",
            description="시험 상태 필터",
            required=False,
            type=str,
            enum=["all", "done", "pending"],
            default="all",
        ),
    ],
    responses={
        200: ExamDeploymentListSerializer,
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                )
            ],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": ErrorMessages.FORBIDDEN.value},
                )
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "코호트 없음/잘못된 요청",
                    value={"error_detail": ErrorMessages.USER_NOT_FOUND.value},
                ),
                OpenApiExample(
                    "잘못된 status",
                    value={"error_detail": ErrorMessages.INVALID_EXAM_LIST_REQUEST.value},
                ),
            ],
        ),
    },
)
class ExamListView(ExamsExceptionMixin, ListAPIView[ExamDeployment]):
    permission_classes = [IsAuthenticated, IsStudentRole]
    serializer_class = ExamDeploymentListSerializer
    pagination_class = SimplePagePagination

    def get_queryset(self) -> QuerySet[ExamDeployment]:
        if getattr(self, "swagger_fake_view", False):
            return ExamDeployment.objects.none()

        user_id = self.request.user.id
        assert user_id is not None
        query_params = self.request.query_params.dict()
        return ExamDeploymentListService.from_request(user_id=user_id, query_params=query_params)
