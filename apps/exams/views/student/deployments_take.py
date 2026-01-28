from __future__ import annotations

from typing import cast

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ErrorMessages
from apps.exams.serializers import TakeExamResponseSerializer
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services import build_take_exam_response, take_exam
from apps.exams.views.mixins import ExamsExceptionMixin
from apps.users.models import User


@extend_schema(
    tags=["exams"],
    summary="시험 응시 문제 조회",
    description="시험 응시 화면에서 필요한 문제 및 상태 정보를 조회합니다.",
    responses={
        200: TakeExamResponseSerializer,
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                ),
            ],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": ErrorMessages.FORBIDDEN.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "시험 정보 없음",
                    value={"error_detail": ErrorMessages.EXAM_NOT_FOUND.value},
                ),
            ],
        ),
        410: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Gone",
            examples=[
                OpenApiExample(
                    "시험 종료",
                    value={"error_detail": ErrorMessages.EXAM_CLOSED.value},
                ),
            ],
        ),
    },
)
class TakeExamAPIView(ExamsExceptionMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, deployment_id: int) -> Response:
        user = cast(User, request.user)
        result = take_exam(user=user, deployment_id=deployment_id)
        payload = build_take_exam_response(result=result)

        return Response(TakeExamResponseSerializer(payload).data, status=status.HTTP_200_OK)
