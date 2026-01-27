from typing import Any, cast

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.serializers.session import (
    ChatbotSessionCreateSerializer,
    ChatbotSessionSerializer,
)
from apps.chatbot.services.session_create import create_chatbot_session
from apps.core.utils.pagination import ChatbotSessionCursorPagination
from apps.users.models import User


class ChatbotSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chatbot"],
        summary="챗봇 세션 목록 조회",
        description="사용자의 챗봇 세션 목록을 조회합니다. (Cursor Pagination 적용)",
    )
    def get(self, request: Request) -> Response:
        user = cast(User, request.user)

        queryset: QuerySet[ChatbotSession] = ChatbotSession.objects.filter(user=user).select_related("question")

        paginator = ChatbotSessionCursorPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = ChatbotSessionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        tags=["chatbot"],
        summary="챗봇 세션 생성",
        request=ChatbotSessionCreateSerializer,
        responses={
            200: ChatbotSessionSerializer,
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
                {"detail": str(exc)},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            ChatbotSessionSerializer(session).data,
            status=status.HTTP_200_OK,
        )
