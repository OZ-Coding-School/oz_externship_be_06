from __future__ import annotations

from typing import cast

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from typing import NoReturn

from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ErrorMessages
from apps.exams.serializers import TakeExamResponseSerializer
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services import build_take_exam_response, take_exam
from apps.users.models import User


class TakeExamAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail=ErrorMessages.UNAUTHORIZED.value)
        raise PermissionDenied(detail=ErrorMessages.FORBIDDEN.value)

    @extend_schema(
        tags=["exams"],
        summary="시험 응시 API",
        description="시험을 응시하고 문제 목록을 조회합니다.",
        responses={
            200: TakeExamResponseSerializer,
            400: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.INVALID_EXAM_SESSION.value),
            401: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.UNAUTHORIZED.value),
            403: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.FORBIDDEN.value),
            404: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.EXAM_NOT_FOUND.value),
        },
    )
    def get(self, request: Request, deployment_id: int) -> Response:
        user = cast(User, request.user)
        result = take_exam(user=user, deployment_id=deployment_id)
        payload = build_take_exam_response(result=result)

        return Response(TakeExamResponseSerializer(payload).data, status=status.HTTP_200_OK)
