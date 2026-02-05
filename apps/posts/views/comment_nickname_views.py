from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.services.comment_nickname_service import generate_comment_nickname


class CommentRandomNicknameAPIView(APIView):
    """
    댓글용 랜덤 닉네임을 반환하는 API
    """

    def get(self, request: Request) -> Response:
        nickname = generate_comment_nickname()
        return Response({"nickname": nickname})
