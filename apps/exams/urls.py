from django.urls import path

from apps.exams.views import TakeExamAPIView

app_name = "exams"

urlpatterns = [
    path("take/", TakeExamAPIView.as_view(), name="take-exam"),
]
