from typing import Any

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.schemas.admin import (
    admin_exam_create_schema,
    admin_exam_list_schema,
)
from apps.exams.views.admin.exams_create import AdminExamCreateAPIView
from apps.exams.views.admin.exams_list import AdminExamListView
from apps.exams.views.mixins import ExamsExceptionMixin


# 어드민 시험 목록 조회/생성
class AdminExamRouterAPIView(ExamsExceptionMixin, APIView):

    @admin_exam_list_schema
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return AdminExamListView.as_view()(request._request, *args, **kwargs)

    @admin_exam_create_schema
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return AdminExamCreateAPIView.as_view()(request._request, *args, **kwargs)
