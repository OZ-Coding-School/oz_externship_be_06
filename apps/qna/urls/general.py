from __future__ import annotations

from django.urls import path

from apps.qna.views import presigned_url_views
from apps.qna.views.answer_views import (
    AIAnswerGenerateAPIView,
    AnswerAdoptAPIView,
    AnswerCommentCreateAPIView,
    AnswerCreateAPIView,
    AnswerUpdateAPIView,
)
from apps.qna.views.category_views import CategoryTreeAPIView
from apps.qna.views.question_views import (
    QuestionCreateListAPIView,
    QuestionDetailAPIView,
)

urlpatterns = [
    # Category
    path("categories", CategoryTreeAPIView.as_view(), name="categories"),
    # Question
    path("questions", QuestionCreateListAPIView.as_view(), name="questions"),
    path("questions/<int:question_id>", QuestionDetailAPIView.as_view(), name="question-detail"),
    # Answer
    path("questions/<int:question_id>/ai-answer", AIAnswerGenerateAPIView.as_view(), name="ai-answer-generate"),
    path("questions/<int:question_id>/answers", AnswerCreateAPIView.as_view(), name="answer-create"),
    path("answers/<int:answer_id>", AnswerUpdateAPIView.as_view(), name="answer-update"),
    path("answers/<int:answer_id>/accept", AnswerAdoptAPIView.as_view(), name="answer-adopt"),
    path("answers/<int:answer_id>/comments", AnswerCommentCreateAPIView.as_view(), name="answer-comment-create"),  # fmt: skip
    # Presigned URL
    path("questions/presigned-url", presigned_url_views.QuestionPresignedUrlAPIView.as_view(), name="question-presigned-url"),
    path("answers/presigned-url", presigned_url_views.AnswerPresignedUrlAPIView.as_view(), name="answer-presigned-url"),
]   # fmt: skip
