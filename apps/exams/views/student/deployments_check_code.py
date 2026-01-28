from __future__ import annotations

from typing import NoReturn, cast

from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ErrorMessages
from apps.exams.models import ExamDeployment
from apps.exams.serializers import CheckCodeRequestSerializer
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.users.models import User


class CheckCodeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail=ErrorMessages.UNAUTHORIZED.value)
        raise PermissionDenied(detail=ErrorMessages.FORBIDDEN.value)

    @extend_schema(
        tags=["exams"],
        summary="참가코드 검증 API",
        description="시험 참가코드를 검증합니다.",
        request=CheckCodeRequestSerializer,
        responses={
            204: OpenApiResponse(description="검증 성공"),
            400: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.INVALID_CHECK_CODE_REQUEST.value),
            401: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.UNAUTHORIZED.value),
            403: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.NO_EXAM_TAKE_PERMISSION.value),
            404: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.DEPLOYMENT_NOT_FOUND.value),
            423: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.EXAM_NOT_AVAILABLE.value),
        },
    )
    def post(self, request: Request, deployment_id: int) -> Response:
        serializer = CheckCodeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            deployment = ExamDeployment.objects.get(id=deployment_id)
        except ExamDeployment.DoesNotExist:
            return Response(
                {"error_detail": ErrorMessages.DEPLOYMENT_NOT_FOUND.value},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 참가 코드 검증
        if deployment.access_code != serializer.validated_data["code"]:
            return Response(
                {"error_detail": ErrorMessages.INVALID_CHECK_CODE_REQUEST.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 권한 확인 (수강생만)
        user = cast(User, request.user)
        if user.role != User.Role.STUDENT:
            return Response(
                {"error_detail": ErrorMessages.NO_EXAM_TAKE_PERMISSION.value},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 시험 상태 확인
        if deployment.status != ExamDeployment.StatusChoices.ACTIVATED:
            return Response(
                {"error_detail": ErrorMessages.INVALID_CHECK_CODE_REQUEST.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 시험 시간 확인
        now = timezone.now()
        if now < deployment.open_at:
            return Response(
                {"error_detail": ErrorMessages.EXAM_NOT_AVAILABLE.value},
                status=status.HTTP_423_LOCKED,
            )
        if now > deployment.close_at:
            return Response(
                {"error_detail": ErrorMessages.EXAM_ALREADY_CLOSED.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 검증 성공 - 204 No Content 반환
        return Response(status=status.HTTP_204_NO_CONTENT)
