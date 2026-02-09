from django.urls import path

from apps.qna.views.admin_category_views import AdminCategoryCreateAPIView
from apps.qna.views.admin_question_views import AdminQuestionDetailAPIView

urlpatterns = [
    # --- Admin QnA Category CRD Endpoints ---
    path("qna/categories", AdminCategoryCreateAPIView.as_view(), name="admin-qna-category-create"),
    # --- Admin QnA CD Endpoints ---
    path("questions/<int:question_id>", AdminQuestionDetailAPIView.as_view(), name="admin-qna-question-detail"),
]
