from __future__ import annotations

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chatbot.models.chatbot_session import ChatbotSession


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
            204: None,  # 삭제 성공 (응답 바디 없음)
            404: None,  # 존재하지 않거나 접근 불가한 세션
        },
    )
    def delete(self, request: Request, session_id: int) -> Response:
        # 본인 세션만 조회 (없거나 권한 없으면 404)
        session = get_object_or_404(
            ChatbotSession,
            pk=session_id,
            user=request.user,
        )

        # 세션 삭제 (연관 메시지는 CASCADE)
        session.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
