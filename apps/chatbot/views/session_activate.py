from typing import Any

from django.core.exceptions import ValidationError
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chatbot.serializers.activate import ChatbotActivateSerializer
from apps.chatbot.serializers.session import ChatbotSessionSerializer
from apps.chatbot.services.session_activate import activate_session


# 문서용 Response Serializer (created 포함)
class _ActivateSessionResponseSerializer(serializers.Serializer[Any]):
    created = serializers.BooleanField()
    session = ChatbotSessionSerializer()


class ChatbotSessionActivateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chatbot"],
        summary="챗봇 세션 활성화",
        description=(
            "채팅 진입 시 사용자와 질문 기준으로 세션을 조회하거나 생성합니다.\n"
            "- 기존 세션이 존재하면 해당 세션을 반환합니다. (200)\n"
            "- 세션이 없으면 새로 생성하여 반환합니다. (201)\n"
            "- 응답 본문은 `created`와 `session` 필드를 포함하며,\n"
            "  `session`은 ChatbotSessionSerializer 형식입니다."
        ),
        request=ChatbotActivateSerializer,
        responses={
            200: _ActivateSessionResponseSerializer,
            201: _ActivateSessionResponseSerializer,
            409: OpenApiResponse(description="이미 응답이 진행 중인 세션입니다."),
        },
    )
    def post(self, request: Request) -> Response:
        # 입력값 검증
        serializer = ChatbotActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # 세션 활성화
            session, created = activate_session(
                user=request.user,
                question_id=serializer.validated_data["question_id"],
            )
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_409_CONFLICT,
            )

        # 응답 반환
        return Response(
            {
                "created": created,
                "session": ChatbotSessionSerializer(session).data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
