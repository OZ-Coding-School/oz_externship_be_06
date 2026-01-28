from django.urls import path

from apps.exams.views.admin.deployments_create import (
    AdminExamDeploymentCreateAPIView,
)
from apps.exams.views.admin.deployments_detail import (
    AdminExamDeploymentDetailAPIView,
)
from apps.exams.views.admin.deployments_status import (
    AdminExamDeploymentStatusAPIView,
)
from apps.exams.views.admin.exams_delete import AdminExamDeleteAPIView
from apps.exams.views.admin.exams_router import AdminExamRouterAPIView
from apps.exams.views.admin.questions_create import AdminExamQuestionCreateAPIView
from apps.exams.views.admin.questions_delete import AdminExamQuestionDeleteAPIView
from apps.exams.views.admin.submissions_list import AdminExamSubmissionListAPIView

urlpatterns = [
    path("exams/<int:exam_id>/questions/", AdminExamQuestionCreateAPIView.as_view(), name="admin-exam-question-create"),
    path("exams/<int:exam_id>/", AdminExamDeleteAPIView.as_view(), name="admin-exam-delete"),
    path("exams", AdminExamRouterAPIView.as_view(), name="admin-exams"),
    path("submissions/", AdminExamSubmissionListAPIView.as_view(), name="admin-exam-submission-list"),
    path(
        "exams/questions/<int:question_id>/",
        AdminExamQuestionDeleteAPIView.as_view(),
        name="admin-exam-question-delete",
    ),
    path("exams/deployments/", AdminExamDeploymentCreateAPIView.as_view(), name="admin-exam-deployment-create"),
    path(
        "exams/deployments/<int:deployment_id>/",
        AdminExamDeploymentDetailAPIView.as_view(),
        name="admin-exam-deployment-detail",
    ),
    path(
        "exams/deployments/<int:deployment_id>/status/",
        AdminExamDeploymentStatusAPIView.as_view(),
        name="admin-exam-deployment-status",
    ),
]
