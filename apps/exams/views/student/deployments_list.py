from __future__ import annotations

from django.db.models import QuerySet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.core.utils.pagination import SimplePagePagination
from apps.core.utils.permissions import IsStudentRole
from apps.exams.models.exam_deployments import ExamDeployment
from apps.exams.schemas.student import exam_deployment_list_schema
from apps.exams.serializers.student.deployments_list import (
    ExamDeploymentListSerializer,
)
from apps.exams.services.student.deployments_list import ExamDeploymentListService
from apps.exams.views.mixins import ExamsExceptionMixin


# 시험 배포 목록 조회
@exam_deployment_list_schema
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
