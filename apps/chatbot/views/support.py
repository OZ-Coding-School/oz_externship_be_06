from typing import cast

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chatbot.serializers.session import ChatbotSessionSerializer
from apps.chatbot.serializers.support import ChatbotSupportSessionCreateSerializer
from apps.chatbot.services.support_create import create_support_session
from apps.users.models import User


class ChatbotSupportSessionCreateAPIView(APIView):
    """시스템 챗봇 세션 생성 (플로팅 버튼 진입)"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chatbot"],
        summary="AI 시스템 챗봇 세션 생성",
        description="플로팅 버튼을 통해 진입하는 시스템용 챗봇 세션을 생성합니다.",
        request=ChatbotSupportSessionCreateSerializer,
        responses={
            200: ChatbotSessionSerializer,
            400: OpenApiResponse(description="유효하지 않은 세션 생성 요청입니다."),
            401: OpenApiResponse(description="로그인한 사용자만 세션 생성을 할 수 있습니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = ChatbotSupportSessionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = cast(User, request.user)

        session = create_support_session(
            user=user,
            title=serializer.validated_data["title"],
            using_model=serializer.validated_data["using_model"],
        )

        return Response(
            ChatbotSessionSerializer(session).data,
            status=status.HTTP_200_OK,
        )
