from django.urls import path

from apps.exams.views.admin.deployments import (
    AdminExamDeploymentCreateAPIView,
)
from apps.exams.views.admin.deployments_status import (
    AdminExamDeploymentStatusAPIView,
)
from apps.exams.views.admin.exams import AdminExamCreateAPIView
from apps.exams.views.admin.exams_delete import AdminExamDeleteAPIView
from apps.exams.views.admin.questions import AdminExamQuestionCreateAPIView
from apps.exams.views.admin.questions_delete import AdminExamQuestionDeleteAPIView
from apps.exams.views.admin.submissions import AdminExamSubmissionListAPIView
from apps.exams.views.admin_exam_deployment_detail_views import (
    AdminExamDeploymentDetailAPIView,
)

urlpatterns = [
    path("exams/<int:exam_id>/questions/", AdminExamQuestionCreateAPIView.as_view(), name="admin-exam-question-create"),
    path("exams/<int:exam_id>/", AdminExamDeleteAPIView.as_view(), name="admin-exam-delete"),
    path("exams", AdminExamCreateAPIView.as_view(), name="admin-exam-create"),
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
