from django.urls import path

from apps.exams.views.exam_list import ExamListView

urlpatterns = [
    path("deployments", ExamListView.as_view(), name="exam-deployments"),
]
