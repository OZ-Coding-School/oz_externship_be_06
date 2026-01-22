from django.urls import path

from apps.exams.views import CheckCodeAPIView, ExamListView, TakeExamAPIView

app_name = "exams"

urlpatterns = [
    path("deployments", ExamListView.as_view(), name="exam-deployments"),
    path("deployments/<int:deployment_id>", TakeExamAPIView.as_view(), name="take-exam"),
    path("deployments/<int:deployment_id>/check_code", CheckCodeAPIView.as_view(), name="check-code"),
]
