from typing import cast

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chatbot.serializers.session import (
    ChatbotSessionCreateSerializer,
    ChatbotSessionSerializer,
)
from apps.chatbot.services.session_create import create_or_activate_chatbot_session
from apps.users.models import User


class ChatbotSessionAPIView(APIView):
    """
    챗봇 세션 API
    - POST /api/v1/chatbot/sessions : 세션 생성 (idempotent)
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ChatbotSessionCreateSerializer

    @extend_schema(
        tags=["chatbot"],
        summary="챗봇 세션 생성",
        description="질문 기준으로 세션을 생성하거나 기존 세션을 반환합니다.",
        request=ChatbotSessionCreateSerializer,
        responses={
            200: ChatbotSessionSerializer,
            400: OpenApiResponse(description="유효하지 않은 요청입니다."),
            404: OpenApiResponse(description="존재하지 않는 질문입니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = ChatbotSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = cast(User, request.user)

        session, _ = create_or_activate_chatbot_session(
            user=user,
            question_id=serializer.validated_data["question"],
            title=serializer.validated_data.get("title"),
            using_model=serializer.validated_data.get("using_model"),
        )

        return Response(
            ChatbotSessionSerializer(session).data,
            status=status.HTTP_200_OK,
        )
