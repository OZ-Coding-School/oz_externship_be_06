from __future__ import annotations

from typing import NoReturn

from django.conf import settings
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.pagination import SimplePagePagination
from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException
from apps.exams.serializers.admin.deployments_list import (
    AdminExamDeploymentListItemSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin.deployments_list import (
    AdminDeploymentListService,
    InvalidAdminDeploymentListParams,
)
from apps.exams.views.mixins import ExamsExceptionMixin


@extend_schema(
    tags=["admin_exams"],
    operation_id="admin_exam_deployments_list",
    summary="어드민 배포 목록 조회",
    description="쪽지시험 배포 내역을 페이지네이션/검색/필터/정렬로 조회합니다.",
    parameters=[
        OpenApiParameter(name="page", required=False, type=int, description="페이지(1부터)"),
        OpenApiParameter(name="size", required=False, type=int, description="페이지 크기"),
        OpenApiParameter(name="search_keyword", required=False, type=str, description="검색어(시험 제목)"),
        OpenApiParameter(name="subject_id", required=False, type=int, description="과목 ID"),
        OpenApiParameter(name="cohort_id", required=False, type=int, description="기수 ID"),
        OpenApiParameter(
            name="sort",
            required=False,
            type=str,
            description="정렬 기준",
            enum=["created_at", "submit_count", "avg_score"],
        ),
        OpenApiParameter(name="order", required=False, type=str, description="정렬 방향", enum=["asc", "desc"]),
    ],
    responses={
        200: OpenApiResponse(description="OK"),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 조회 요청",
                    value={"error_detail": ErrorMessages.INVALID_DEPLOYMENT_LIST_REQUEST.value},
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[OpenApiExample("인증 실패", value={"error_detail": ErrorMessages.UNAUTHORIZED.value})],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": ErrorMessages.NO_DEPLOYMENT_LIST_PERMISSION.value},
                )
            ],
        ),
    },
)
class AdminExamDeploymentListAPIView(ExamsExceptionMixin, APIView):
    """어드민 쪽지시험 배포 목록 조회 API."""

    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = AdminExamDeploymentListItemSerializer
    pagination_class = SimplePagePagination

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=ErrorMessages.NO_DEPLOYMENT_LIST_PERMISSION.value)

    def get(self, request: Request) -> Response:
        qp = request.query_params
        if settings.USE_EXAM_MOCK:
            payload = [
                {
                    "id": 77,
                    "submit_count": 58,
                    "avg_score": 72.3,
                    "status": "Activated",
                    "exam": {
                        "id": 101,
                        "title": "Python 기본 문법 테스트",
                        "thumbnail_img_url": "https://img.com/images/sample.png",
                    },
                    "subject": {"id": 10, "name": "Python"},
                    "cohort": {
                        "id": 21,
                        "number": 12,
                        "display": "백엔드 12기",
                        "course": {"id": 23, "name": "Backend Bootcamp", "tag": "BE"},
                    },
                    "created_at": "2025-03-01 14:20:33",
                }
            ]
            paginator = self.pagination_class()
            paginated_payload: list[dict[str, object]] | None = paginator.paginate_queryset(payload, request)  # type: ignore[arg-type]
            return paginator.get_paginated_response(paginated_payload)

        try:
            params = AdminDeploymentListService.parse_params(
                search_keyword=qp.get("search_keyword"),
                subject_id=qp.get("subject_id"),
                cohort_id=qp.get("cohort_id"),
                sort=qp.get("sort"),
                order=qp.get("order"),
            )
        except InvalidAdminDeploymentListParams as exc:
            raise ErrorDetailException(str(exc), status.HTTP_400_BAD_REQUEST) from exc

        queryset = AdminDeploymentListService.get_queryset(params)

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
