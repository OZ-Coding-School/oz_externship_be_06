from typing import NoReturn

from django.db.models import QuerySet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from apps.core.utils.pagination import AdminExamPagination
from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import Exam
from apps.exams.serializers.admin.exams_list import AdminExamListItemSerializer
from apps.exams.services.admin.exams_list import (
    AdminExamListService,
    InvalidAdminExamListParams,
)
from apps.exams.views.mixins import ExamsExceptionMixin


class AdminExamListView(ExamsExceptionMixin, ListAPIView[Exam]):
    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = AdminExamListItemSerializer
    pagination_class = AdminExamPagination

    def permission_denied(
        self,
        request: Request,
        message: str | None = None,
        code: str | None = None,
    ) -> NoReturn:
        from rest_framework.exceptions import NotAuthenticated, PermissionDenied

        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=ErrorMessages.NO_EXAM_LIST_PERMISSION.value)

    def get_queryset(self) -> QuerySet[Exam]:
        qp = self.request.query_params

        try:
            params = AdminExamListService.parse_params(
                search_keyword=qp.get("search_keyword"),
                subject_id=qp.get("subject_id"),
                sort=qp.get("sort"),
                order=qp.get("order"),
            )
        except InvalidAdminExamListParams as exc:
            raise_error(ErrorMessages.INVALID_EXAM_LIST_REQUEST)
        return AdminExamListService.get_queryset(params)
