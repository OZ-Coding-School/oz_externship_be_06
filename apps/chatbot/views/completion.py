from __future__ import annotations

import json
from typing import Iterator, Union

from django.core.cache import cache
from django.http import StreamingHttpResponse
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chatbot.models.chatbot_completions import ChatbotCompletions
from apps.chatbot.models.chatbot_session import ChatbotSession
from apps.chatbot.services.completion_answer import generate_completion_answer


def sse(payload: str) -> str:
    return f"data: {payload}\n\n"


class ChatbotCompletionCreateAPIView(APIView):
    """
    POST /api/v1/chatbot/sessions/{session_id}/completions
    """

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
        # 1. 권한 및 입력값 검증
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"error_detail": "로그인한 사용자만 채팅할 수 있습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        message = request.data.get("message")
        if not message or not isinstance(message, str) or not message.strip():
            return Response({"message": "유효한 메시지를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = ChatbotSession.objects.get(id=session_id, user=request.user)
        except ChatbotSession.DoesNotExist:
            return Response({"error_detail": "챗봇 세션이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 2. 중복 요청 방지 (Redis Lock)
        lock_key = f"chatbot:responding:{session.id}"
        if not cache.add(lock_key, "1", timeout=180):
            return Response({"message": "현재 답변 생성 중입니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 3. 사용자 질문 DB 저장 (선행)
            ChatbotCompletions.objects.create(
                session=session,
                content=message,
                role=ChatbotCompletions.Role.USER,
            )

            # 4. 스트리밍 Generator 정의
            def stream() -> Iterator[str]:
                full_answer = ""
                try:
                    # Service로부터 실시간 chunk 수신
                    for chunk in generate_completion_answer(session=session, user_message=message):
                        full_answer += chunk
                        yield sse(json.dumps({"content": chunk}, ensure_ascii=False))

                    # 5. 응답 완료 후 Assistant 답변 DB 저장
                    if full_answer:
                        ChatbotCompletions.objects.create(
                            session=session,
                            content=full_answer,
                            role=ChatbotCompletions.Role.ASSISTANT,
                        )

                    yield sse("[DONE]")

                except Exception as e:
                    # 스트리밍 도중 에러 발생 시 클라이언트에 알림
                    print(f"DEBUG ERROR: {e}")
                    yield sse(json.dumps({"error": f"상세 에러: {str(e)}"}, ensure_ascii=False))
                    # yield sse(json.dumps({"error": "응답 생성 중 오류 발생"}, ensure_ascii=False))
                finally:
                    cache.delete(lock_key)

            # 6. Response 반환
            response = StreamingHttpResponse(stream(), content_type="text/event-stream; charset=utf-8")
            response.status_code = status.HTTP_201_CREATED
            response["Cache-Control"] = "no-cache"
            response["X-Accel-Buffering"] = "no"  # Nginx 버퍼링 방지
            return response

        except Exception:
            cache.delete(lock_key)
            raise
