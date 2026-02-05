from django.urls import path

from apps.qna.views import presigned_url_view
from apps.qna.views.answer_view import AIAnswerGenerateAPIView, AnswerCreateAPIView
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
    path("questions/<int:question_id>/ai-answer", AIAnswerGenerateAPIView.as_view(), name="ai-answer-generate"),
    # --- Presigned URL Endpoints ---
    path("questions/presigned-url", presigned_url_view.QuestionPresignedUrlAPIView.as_view(), name="question-presigned-url"),
    path("answers/presigned-url", presigned_url_view.AnswerPresignedUrlAPIView.as_view(), name="answer-presigned-url"),
]   # fmt: skip

