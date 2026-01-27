from __future__ import annotations

from typing import cast

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.serializers import TakeExamResponseSerializer
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services import build_take_exam_response, take_exam
from apps.users.models import User


class TakeExamAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["exams"],
        summary="시험 응시 API",
        description="시험을 응시하고 문제 목록을 조회합니다.",
        responses={
            200: TakeExamResponseSerializer,
            400: OpenApiResponse(ErrorResponseSerializer, description="유효하지 않은 요청"),
            401: OpenApiResponse(ErrorResponseSerializer, description="인증 실패"),
            403: OpenApiResponse(ErrorResponseSerializer, description="응시 권한 없음"),
            404: OpenApiResponse(ErrorResponseSerializer, description="시험 정보 없음"),
        },
    )
    def get(self, request: Request, deployment_id: int) -> Response:
        user = cast(User, request.user)
        result = take_exam(user=user, deployment_id=deployment_id)
        payload = build_take_exam_response(result=result)

        return Response(TakeExamResponseSerializer(payload).data, status=status.HTTP_200_OK)
