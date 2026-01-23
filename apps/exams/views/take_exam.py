from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.services import build_take_exam_response, take_exam


class TakeExamAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, deployment_id: int) -> Response:
        result = take_exam(user=request.user, deployment_id=deployment_id)
        payload = build_take_exam_response(result=result)
        return Response(payload, status=200)
