from __future__ import annotations

from typing import cast

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ErrorMessages
from apps.exams.models import ExamDeployment
from apps.exams.serializers import CheckCodeRequestSerializer
from apps.exams.services.student.deployments_status import (
    is_deployment_activated,
    is_deployment_opened,
    is_deployment_time_closed,
)
from apps.exams.views.mixins import ExamsExceptionMixin
from apps.users.models import User


class CheckCodeAPIView(ExamsExceptionMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, deployment_id: int) -> Response:
        serializer = CheckCodeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
        if not is_deployment_activated(deployment):
            return Response(
                {"error_detail": ErrorMessages.INVALID_CHECK_CODE_REQUEST.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 시험 시간 확인
        now = timezone.now()
        if not is_deployment_opened(deployment, now=now):
            return Response(
                {"error_detail": ErrorMessages.EXAM_NOT_AVAILABLE.value},
                status=status.HTTP_423_LOCKED,
            )
        if is_deployment_time_closed(deployment, now=now):
            return Response(
                {"error_detail": ErrorMessages.EXAM_ALREADY_CLOSED.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 검증 성공 - 204 No Content 반환
        return Response(status=status.HTTP_204_NO_CONTENT)
