from django.urls import path

from apps.qna.views.question_view import (
    QuestionCreateListAPIView,
    QuestionDetailAPIView,
)

urlpatterns = [
    path("questions", QuestionCreateListAPIView.as_view(), name="question-list-create"),
    path("questions/<int:question_id>", QuestionDetailAPIView.as_view(), name="question-detail"),
]
