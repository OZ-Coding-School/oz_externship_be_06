from django.urls import path

from apps.exams.views import CheckCodeAPIView, ExamListView, TakeExamAPIView
from apps.exams.views.cheating_views import ExamCheatingUpdateAPIView
from apps.exams.views.exam_submission import ExamSubmissionCreateAPIView
from apps.exams.views.exam_result import ExamSubmissionDetailView
from apps.exams.views.status_views import ExamStatusCheckAPIView
from apps.exams.views.exam_submission import ExamSubmissionCreateView
from apps.exams.views.status_views import ExamStatusCheckAPIView

app_name = "exams"

urlpatterns = [
    path("deployments", ExamListView.as_view(), name="exam-deployments"),
    path("deployments/<int:deployment_id>", TakeExamAPIView.as_view(), name="take-exam"),
    path("deployments/<int:deployment_id>/check_code", CheckCodeAPIView.as_view(), name="check-code"),
    path("deployments/<int:deployment_id>/status/", ExamStatusCheckAPIView.as_view(), name="exam-status"),
    path("deployments/<int:deployment_id>/cheating/", ExamCheatingUpdateAPIView.as_view(), name="exam-cheating"),
    path("submissions", ExamSubmissionCreateAPIView.as_view(), name="exam-submission-create"),
    path("submissions", ExamSubmissionCreateView.as_view(), name="exam-submission-create"),
    path("api/v1/exams/submissions", ExamSubmissionCreateView.as_view(), name="exam-submission-create"),
    path("submissions/<int:submission_id>", ExamSubmissionDetailView.as_view(), name="exam-result"),
]
