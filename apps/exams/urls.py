# exams/urls.py
from django.urls import path

from apps.exams.views.exam_list import ExamListView

urlpatterns = [
    path("api/v1/exams/deployments", ExamListView.as_view(), name="exam-deployments"),
]
