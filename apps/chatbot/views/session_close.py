from __future__ import annotations

from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.session_close import close_session
from apps.users.models import User


@extend_schema(
    tags=["chatbot"],
    summary="챗봇 세션 닫기",
    description="챗봇 대화창 닫기 시 세션 종료 처리",
    responses={
        204: None,
        403: {"error_detail": "삭제 권한이 없습니다."},
        404: {"error_detail": "챗봇 세션이 존재하지 않습니다."},
    },
)
class ChatbotSessionCloseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, session_id: int) -> Response:
        user = cast(User, request.user)

        try:
            close_session(user=user, session_id=session_id)
        except ChatbotSession.DoesNotExist:
            return Response(
                {"error_detail": "챗봇 세션이 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionError:
            return Response(
                {"error_detail": "삭제 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
