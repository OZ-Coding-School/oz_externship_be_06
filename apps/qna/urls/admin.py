from django.urls import path

from apps.qna.views.admin.admin_answer_view import AdminAnswerDeleteAPIView
from apps.qna.views.admin.admin_category_views import (
    AdminCategoriesAPIView,
    AdminCategoryDeleteAPIView,
)
from apps.qna.views.admin.admin_question_views import (
    AdminQuestionDetailAPIView,
    AdminQuestionListAPIView,
)

urlpatterns = [
    # --- Admin QnA-Category ---
    path("qna/categories", AdminCategoriesAPIView.as_view(), name="admin-qna-categories"),
    path("qna/categories/<int:category_id>", AdminCategoryDeleteAPIView.as_view(), name="admin-qna-category-delete"),
    # --- Admin QnA-Question---
    path("qna/questions", AdminQuestionListAPIView.as_view(), name="admin-qna-questions"),
    path("qna/questions/<int:question_id>", AdminQuestionDetailAPIView.as_view(), name="admin-qna-question-detail"),
    # --- Admin QnA-Answer ---
    path("qna/answers/<int:answer_id>", AdminAnswerDeleteAPIView.as_view(), name="admin-qna-answer-delete"),
]
