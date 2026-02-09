from django.urls import path

from apps.qna.views.admin_question_views import AdminQuestionDetailAPIView

urlpatterns = [
    path("questions/<int:question_id>", AdminQuestionDetailAPIView.as_view(), name="admin-qna-question-detail"),
]
