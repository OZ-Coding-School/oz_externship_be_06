from django.urls import path

from apps.exams.views.admin_question_views import AdminExamQuestionCreateAPIView

urlpatterns = [
    path("<int:exam_id>/questions/", AdminExamQuestionCreateAPIView.as_view(), name="admin-exam-question-create"),
]
