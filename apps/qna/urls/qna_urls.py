from django.urls import path

from apps.qna.views.answer_view import AnswerCreateAPIView
from apps.qna.views.question_view import (
    QuestionCategoryTreeAPIView,
    QuestionCreateListAPIView,
    QuestionDetailAPIView,
)

urlpatterns = [
    # --- QnA URL Endpoints ---
    path("questions", QuestionCreateListAPIView.as_view(), name="question-list-create"),
    path("questions/<int:question_id>", QuestionDetailAPIView.as_view(), name="question-detail"),
    path("questions/<int:question_id>/answers", AnswerCreateAPIView.as_view(), name="answer-create"),
    path("categories", QuestionCategoryTreeAPIView.as_view(), name="question-category-list"),
]
