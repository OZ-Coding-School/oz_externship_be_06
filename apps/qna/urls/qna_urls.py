from django.urls import path

from apps.qna.views import presigned_url_views
from apps.qna.views.answer_views import (
    AIAnswerGenerateAPIView,
    AnswerAdoptAPIView,
    AnswerCommentCreateAPIView,
    AnswerCreateAPIView,
)
from apps.qna.views.question_views import (
    QuestionCategoryTreeAPIView,
    QuestionCreateListAPIView,
    QuestionDetailAPIView,
)

urlpatterns = [
    # --- QnA URL Endpoints ---
    # Question
    path("questions", QuestionCreateListAPIView.as_view(), name="question-list-create"),
    path("questions/<int:question_id>", QuestionDetailAPIView.as_view(), name="question-detail"),
    path("categories", QuestionCategoryTreeAPIView.as_view(), name="question-category-list"),
    # Answer
    path("questions/<int:question_id>/ai-answer", AIAnswerGenerateAPIView.as_view(), name="ai-answer-generate"),
    path("questions/<int:question_id>/answers", AnswerCreateAPIView.as_view(), name="answer-create"),
    path("answers/<int:answer_id>/accept", AnswerAdoptAPIView.as_view(), name="answer-adopt"),
    path("answers/<int:answer_id>/comments", AnswerCommentCreateAPIView.as_view(), name="answer-comment-create"),  # fmt: skip
    # --- Presigned URL Endpoints ---
    path("questions/presigned-url", presigned_url_views.QuestionPresignedUrlAPIView.as_view(), name="question-presigned-url"),
    path("answers/presigned-url", presigned_url_views.AnswerPresignedUrlAPIView.as_view(), name="answer-presigned-url"),
]   # fmt: skip
