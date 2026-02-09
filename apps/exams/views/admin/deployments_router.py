from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.schemas.admin import (
    admin_exam_deployment_router_create_schema,
    admin_exam_deployment_router_list_schema,
)
from apps.exams.views.admin.deployments_create import (
    AdminExamDeploymentCreateAPIView,
)
from apps.exams.views.admin.deployments_list import (
    AdminExamDeploymentListAPIView,
)
from apps.exams.views.mixins import ExamsExceptionMixin


# 어드민 배포 목록 조회 / 어드민 배포 생성
class AdminExamDeploymentRouterAPIView(ExamsExceptionMixin, APIView):
    @admin_exam_deployment_router_list_schema
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return AdminExamDeploymentListAPIView.as_view()(request._request, *args, **kwargs)

    @admin_exam_deployment_router_create_schema
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return AdminExamDeploymentCreateAPIView.as_view()(request._request, *args, **kwargs)
