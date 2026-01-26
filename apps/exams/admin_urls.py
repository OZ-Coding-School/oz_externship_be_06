from django.urls import path

from apps.exams.views.admin_exam_delete_views import AdminExamDeleteAPIView
from apps.exams.views.admin_exam_views import AdminExamCreateAPIView
from apps.exams.views.admin_question_views import AdminExamQuestionCreateAPIView
from apps.exams.views.admin_submission_views import AdminExamSubmissionListAPIView

urlpatterns = [
    path("exams/<int:exam_id>/questions/", AdminExamQuestionCreateAPIView.as_view(), name="admin-exam-question-create"),
    path("exams/<int:exam_id>/", AdminExamDeleteAPIView.as_view(), name="admin-exam-delete"),
    path("exams", AdminExamCreateAPIView.as_view(), name="admin-exam-create"),
    path("submissions/", AdminExamSubmissionListAPIView.as_view(), name="admin-exam-submission-list"),
]
