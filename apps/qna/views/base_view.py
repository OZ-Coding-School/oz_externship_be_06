from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.exceptions.handler import qna_exception_handler
from apps.qna.utils.model_types import User


class QnaBaseAPIView(APIView):
    """
    QnA 앱의 모든 View가 상속받을 베이스 뷰
    이 뷰를 상속받으면 settings.py를 건드리지 않고도 QnA 전용 에러 규격이 적용됨
    """

    @property
    def request_user(self) -> User:
        """
        매번 cast나 isinstance를 하지 않도록 인증된 사용자를 반환하는 전용 프로퍼티
        인증되지 않은 사용자가 접근할 경우 DRF의 NotAuthenticated 예외를 발생
        """
        user = self.request.user

        # IsAuthenticated 권한 클래스가 체크해주지만,
        # Mypy 타입을 확정하고 런타임 안전성을 위해 한 번 더 체크
        if not isinstance(user, User):
            raise NotAuthenticated()

        return user

    def handle_exception(self, exc: Exception) -> Response:
        response = qna_exception_handler(exc, self.get_renderer_context())
        if response is None:
            raise exc
        response.exception = True
        return response
