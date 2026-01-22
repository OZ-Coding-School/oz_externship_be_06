from django.urls import path

from apps.qna.views.question_view import QuestionCreateAPIView

urlpatterns = [
    # 엔드포인트는 동일하게 유지하되 APIView 클래스 연결
    path("questions", QuestionCreateAPIView.as_view(), name="question-create"),
]
