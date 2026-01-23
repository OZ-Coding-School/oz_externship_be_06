from __future__ import annotations

from typing import cast

from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.serializers import TakeExamRequestSerializer, TakeExamResponseSerializer
from apps.exams.services import build_take_exam_response, take_exam
from apps.users.models import User


class TakeExamAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, deployment_id: int) -> Response:
        user = cast(User, request.user)
        result = take_exam(user=user, deployment_id=deployment_id)
        payload = build_take_exam_response(result=result)

        return Response(TakeExamResponseSerializer(payload).data, status=200)
