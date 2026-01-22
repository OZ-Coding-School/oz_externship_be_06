from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chatbot.serializers.activate import ChatbotActivateSerializer
from apps.chatbot.serializers.session import ChatbotSessionSerializer
from apps.chatbot.services.session_activate import activate_session


class ChatbotSessionActivateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = ChatbotActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            session, created = activate_session(
                user=request.user,
                question_id=serializer.validated_data["question_id"],
            )
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_409_CONFLICT,
            )

        response_serializer = ChatbotSessionSerializer(session)
        result = response_serializer.data
        result["created"] = created

        return Response(
            result,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
