from __future__ import annotations

from typing import NoReturn

from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.pagination import SimplePagePagination
from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.schemas.admin import admin_exam_deployment_list_schema
from apps.exams.serializers.admin.deployments_list import (
    AdminExamDeploymentListItemSerializer,
)
from apps.exams.services.admin.deployments_list import (
    AdminDeploymentListService,
    InvalidAdminDeploymentListParams,
)
from apps.exams.views.mixins import ExamsExceptionMixin


@admin_exam_deployment_list_schema
class AdminExamDeploymentListAPIView(ExamsExceptionMixin, APIView):
    # 어드민 배포 목록 조회
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
        try:
            params = AdminDeploymentListService.parse_params(
                search_keyword=qp.get("search_keyword"),
                subject_id=qp.get("subject_id"),
                cohort_id=qp.get("cohort_id"),
                sort=qp.get("sort"),
                order=qp.get("order"),
            )
        except InvalidAdminDeploymentListParams as exc:
            raise_error(ErrorMessages.INVALID_DEPLOYMENT_LIST_REQUEST)

        queryset = AdminDeploymentListService.get_queryset(params)

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
