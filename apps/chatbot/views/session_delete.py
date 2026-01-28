from __future__ import annotations

from typing import cast

from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chatbot.services.session_delete import delete_chatbot_session
from apps.users.models import User


class ChatbotSessionDeleteAPIView(APIView):
    """챗봇 세션 삭제 API"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chatbot"],
        summary="챗봇 세션 삭제",
        description=(
            "특정 챗봇 세션을 삭제합니다.\n"
            "- 본인이 생성한 세션만 삭제 가능합니다.\n"
            "- 권한이 없거나 존재하지 않는 세션은 404를 반환합니다."
        ),
        responses={
            204: None,
            404: None,
        },
    )
    def delete(self, request: Request, session_id: int) -> Response:
        user = cast(User, request.user)

        try:
            delete_chatbot_session(
                user=user,
                session_id=session_id,
            )
        except ValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
