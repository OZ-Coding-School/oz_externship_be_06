from django.urls import path

from apps.qna.views.admin_question_views import AdminQuestionListAPIView

urlpatterns = [
    path("qna/questions", AdminQuestionListAPIView.as_view(), name="admin-qna-question-list"),
]
