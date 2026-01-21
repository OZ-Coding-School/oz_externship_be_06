from django.urls import path

from apps.exams.views.cheating_views import ExamCheatingUpdateAPIView
from apps.exams.views.status_views import ExamStatusCheckAPIView
from apps.exams.views.exam_list import ExamListView


urlpatterns = [
    path("deployments/<int:deployment_id>/status/", ExamStatusCheckAPIView.as_view(), name="exam-status"),
    path("deployments/<int:deployment_id>/cheating/", ExamCheatingUpdateAPIView.as_view(), name="exam-cheating"),
    path("deployments", ExamListView.as_view(), name="exam-deployments"),
    path("api/v1/exams/deployments", ExamListView.as_view(), name="exam-deployments"),
]
