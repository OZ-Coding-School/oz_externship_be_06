from django.urls import path

from apps.qna.views.question_view import QuestionCreateListAPIView

urlpatterns = [
    path("questions", QuestionCreateListAPIView.as_view(), name="question-list-create"),
]
