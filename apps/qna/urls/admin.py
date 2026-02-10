from django.urls import path

from apps.qna.views.admin.admin_category_views import AdminCategoriesAPIView
from apps.qna.views.admin.admin_question_views import AdminQuestionDetailAPIView

urlpatterns = [
    # --- Admin QnA Category CRD Endpoints ---
    path("qna/categories", AdminCategoriesAPIView.as_view(), name="admin-qna-categories"),
    # --- Admin QnA CD Endpoints ---
    path("qna/questions/<int:question_id>", AdminQuestionDetailAPIView.as_view(), name="admin-qna-question-detail"),
]
