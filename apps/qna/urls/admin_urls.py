from django.urls import path

from apps.qna.views.admin_question_views import AdminQuestionDeleteAPIView

urlpatterns = [
    path("qna/questions/<int:question_id>", AdminQuestionDeleteAPIView.as_view(), name="admin-qna-question-delete"),
]
