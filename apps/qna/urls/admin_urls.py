from django.urls import path

from apps.qna.views.admin_answer_view import AdminAnswerDeleteAPIView

urlpatterns = [
    path("answers/<int:answer_id>", AdminAnswerDeleteAPIView.as_view(), name="admin-qna-answer-delete"),
]
