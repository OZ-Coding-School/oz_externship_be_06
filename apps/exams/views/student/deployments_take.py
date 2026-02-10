from __future__ import annotations

from typing import cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ErrorMessages
from apps.exams.schemas.student import take_exam_schema
from apps.exams.serializers import TakeExamResponseSerializer
from apps.exams.services import build_take_exam_response, take_exam
from apps.exams.validators import parse_positive_int
from apps.exams.views.mixins import ExamsExceptionMixin
from apps.users.models import User


@take_exam_schema
class TakeExamAPIView(ExamsExceptionMixin, APIView):
    # 시험 응시 문제 조회
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, deployment_id: int) -> Response:
        parse_positive_int(deployment_id, ErrorMessages.EXAM_NOT_FOUND)
        user = cast(User, request.user)
        result = take_exam(user=user, deployment_id=deployment_id)
        payload = build_take_exam_response(result=result)

        return Response(TakeExamResponseSerializer(payload).data, status=status.HTTP_200_OK)
