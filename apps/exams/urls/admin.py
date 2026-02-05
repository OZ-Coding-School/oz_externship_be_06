from django.urls import path

from apps.exams.views.admin.deployments_detail import (
    AdminExamDeploymentDetailAPIView,
)
from apps.exams.views.admin.deployments_router import (
    AdminExamDeploymentRouterAPIView,
)
from apps.exams.views.admin.deployments_status import (
    AdminExamDeploymentStatusAPIView,
)
from apps.exams.views.admin.exams_detail import AdminExamDetailAPIView
from apps.exams.views.admin.exams_router import AdminExamRouterAPIView
from apps.exams.views.admin.presigned_url_view import ExamPresignedUrlAPIView
from apps.exams.views.admin.questions_create import AdminExamQuestionCreateAPIView
from apps.exams.views.admin.questions_delete import AdminExamQuestionDeleteAPIView
from apps.exams.views.admin.submissions_detail import AdminExamSubmissionDetailAPIView
from apps.exams.views.admin.questions_detail import AdminExamQuestionDetailAPIView
from apps.exams.views.admin.submissions_delete import AdminExamSubmissionDeleteAPIView
from apps.exams.views.admin.submissions_list import AdminExamSubmissionListAPIView

urlpatterns = [
    path("exams/<int:exam_id>/questions/", AdminExamQuestionCreateAPIView.as_view(), name="admin-exam-question-create"),
    # put + delete
    path("exams/<int:exam_id>/", AdminExamDetailAPIView.as_view(), name="admin-exam-detail"),
    path("exams", AdminExamRouterAPIView.as_view(), name="admin-exams"),
    path(
        "exams/presigned-url/thumbnail/",
        ExamPresignedUrlAPIView.as_view(),
        name="exam-presigned-url",
    ),
    path("submissions/", AdminExamSubmissionListAPIView.as_view(), name="admin-exam-submission-list"),
    path(
        "exams/questions/<int:question_id>/",
        AdminExamQuestionDetailAPIView.as_view(),
        name="admin-exam-question-detail",
    ),
    path("exams/deployments/", AdminExamDeploymentRouterAPIView.as_view(), name="admin-exam-deployments"),
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
    path(
        "exams/submissions/<int:submission_id>/",
        AdminExamSubmissionDetailAPIView.as_view(),
        name="admin-exam-submission-detail",
    ),
]
