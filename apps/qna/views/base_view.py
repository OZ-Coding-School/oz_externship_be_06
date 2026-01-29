from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.exceptions.base_e import qna_exception_handler


class QnaBaseAPIView(APIView):
    """
    QnA 앱의 모든 View가 상속받을 베이스 뷰.
    이 뷰를 상속받으면 settings.py를 건드리지 않고도 QnA 전용 에러 규격이 적용됩니다.
    """

    def handle_exception(self, exc: Exception) -> Response:
        response = qna_exception_handler(exc, self.get_renderer_context())
        if response is None:
            raise exc
        response.exception = True
        return response
