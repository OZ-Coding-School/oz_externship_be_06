from __future__ import annotations

from typing import cast

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.schemas.student import check_code_schema
from apps.exams.serializers import CheckCodeRequestSerializer
from apps.exams.services.student.deployments_status import (
    get_deployment_or_404,
    validate_deployment_active,
)
from apps.exams.views.mixins import ExamsExceptionMixin
from apps.users.models import User


# 시험 참가 코드 검증
@check_code_schema
class CheckCodeAPIView(ExamsExceptionMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, deployment_id: int) -> Response:
        serializer = CheckCodeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deployment = get_deployment_or_404(deployment_id)

        # 참가 코드 검증
        if deployment.access_code != serializer.validated_data["code"]:
            raise_error(ErrorMessages.INVALID_CHECK_CODE_REQUEST)

        # 권한 확인 (수강생만)
        user = cast(User, request.user)
        if user.role != User.Role.STUDENT:
            raise_error(ErrorMessages.NO_EXAM_TAKE_PERMISSION)

        validate_deployment_active(deployment, now=timezone.now())

        # 검증 성공 - 204 No Content 반환
        return Response(status=status.HTTP_204_NO_CONTENT)
