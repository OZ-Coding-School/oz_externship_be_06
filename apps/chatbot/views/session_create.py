from typing import cast

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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
from apps.chatbot.services.session_create import create_chatbot_session


class ChatbotSessionCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Chatbot"],
        summary="챗봇 세션 생성",
        request=ChatbotSessionCreateSerializer,
        responses={
            201: ChatbotSessionSerializer,
            409: OpenApiResponse(description="이미 존재하는 세션"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = ChatbotSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = cast(User, request.user)
        try:
            session = create_chatbot_session(
                user=user,
                question_id=serializer.validated_data["question_id"],
                title=serializer.validated_data.get("title"),
                using_model=serializer.validated_data.get("using_model"),
            )
        except ValidationError as exc:
            return Response(
                {"detail": exc.message},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            ChatbotSessionSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )
