from __future__ import annotations

import json
from typing import Iterator, Union, cast

from django.core.cache import cache
from django.http import StreamingHttpResponse
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chatbot.constants.question_prompts import QUESTION_SYSTEM_PROMPT
from apps.chatbot.constants.support_prompts import SUPPORT_FULL_PROMPT
from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.serializers.completion import ChatbotCompletionCreateSerializer
from apps.chatbot.services.completion_answer import generate_completion_answer
from apps.chatbot.services.question_completion_policy import (
    validate_user_prompt_policy as validate_question_policy,
)
from apps.chatbot.services.support_completion_policy import (
    validate_user_prompt_policy as validate_support_policy,
)
from apps.users.models import User


def sse(payload: str) -> str:
    return f"data: {payload}\n\n"


class ChatbotCompletionCreateAPIView(APIView):
    """
    POST /api/v1/chatbot/sessions/{session_id}/completions
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["chatbot"],
        summary="AI 챗봇 응답 생성 API",
        description="AI 답변을 SSE 스트리밍으로 전송합니다.",
        request={
            "application/json": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            }
        },
        responses={
            201: OpenApiResponse(
                description="SSE 스트리밍 응답",
                examples=[
                    OpenApiExample(
                        "SSE stream",
                        value='data: {"content": "안"}\n\n' 'data: {"content": "녕"}\n\n' "data: [DONE]\n\n",
                        media_type="text/event-stream",
                    )
                ],
            ),
            400: OpenApiResponse(description="잘못된 요청"),
            401: OpenApiResponse(description="인증 실패"),
            404: OpenApiResponse(description="세션 없음"),
        },
    )
    def post(self, request: Request, session_id: int) -> Union[Response, StreamingHttpResponse]:
        serializer = ChatbotCompletionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message = serializer.validated_data["message"]

        try:
            user = cast(User, request.user)
            session = ChatbotSession.objects.get(id=session_id, user=user)
        except ChatbotSession.DoesNotExist:
            return Response(
                {"error_detail": "챗봇 세션이 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        lock_key = f"chatbot:responding:{session.id}"

        if not cache.get(lock_key):
            last = ChatbotCompletions.objects.filter(session=session).order_by("-created_at").first()
            if last and last.role == ChatbotCompletions.Role.USER:
                last.delete()

        try:
            if session.question_id is not None:
                validate_question_policy(session=session, content=message)
            else:
                validate_support_policy(session=session, content=message)
        except ValidationError as exc:
            return Response(
                {"error_detail": exc.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not cache.add(lock_key, "1", timeout=180):
            return Response(
                {"error_detail": "현재 답변 생성 중입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_completion = ChatbotCompletions.objects.create(
                session=session,
                content=message,
                role=ChatbotCompletions.Role.USER,
            )

            system_prompt = SUPPORT_FULL_PROMPT if session.question_id is None else QUESTION_SYSTEM_PROMPT

            def stream() -> Iterator[str]:
                full_answer = ""
                try:
                    for chunk in generate_completion_answer(
                        session=session,
                        system_prompt=system_prompt,
                    ):
                        full_answer += chunk
                        yield sse(json.dumps({"content": chunk}, ensure_ascii=False))

                    if full_answer:
                        ChatbotCompletions.objects.create(
                            session=session,
                            content=full_answer,
                            role=ChatbotCompletions.Role.ASSISTANT,
                        )

                    yield sse("[DONE]")

                except Exception as exc:
                    print(f"DEBUG ERROR: {exc}")
                    user_completion.delete()
                    yield sse(
                        json.dumps(
                            {"error_detail": "응답 생성 중 오류가 발생했습니다."},
                            ensure_ascii=False,
                        )
                    )
                finally:
                    cache.delete(lock_key)

            response = StreamingHttpResponse(
                stream(),
                content_type="text/event-stream; charset=utf-8",
            )
            response.status_code = status.HTTP_201_CREATED
            response["Cache-Control"] = "no-cache"
            response["X-Accel-Buffering"] = "no"
            return response

        except Exception:
            cache.delete(lock_key)
            raise
