from __future__ import annotations

from typing import cast

from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.models import ExamDeployment
from apps.exams.serializers import CheckCodeRequestSerializer
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.users.models import User


class CheckCodeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["exams"],
        summary="참가코드 검증 API",
        description="시험 참가코드를 검증합니다.",
        request=CheckCodeRequestSerializer,
        responses={
            204: OpenApiResponse(description="검증 성공"),
            400: OpenApiResponse(ErrorResponseSerializer, description="유효하지 않은 코드 또는 시험 상태"),
            401: OpenApiResponse(ErrorResponseSerializer, description="인증 실패"),
            403: OpenApiResponse(ErrorResponseSerializer, description="응시 권한 없음"),
            404: OpenApiResponse(ErrorResponseSerializer, description="시험 정보 없음"),
            423: OpenApiResponse(ErrorResponseSerializer, description="시험 시작 시간 전"),
        },
    )
    def post(self, request: Request, deployment_id: int) -> Response:
        serializer = CheckCodeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            deployment = ExamDeployment.objects.get(id=deployment_id)
        except ExamDeployment.DoesNotExist:
            return Response(
                {"error_detail": "해당 시험 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 참가 코드 검증
        if deployment.access_code != serializer.validated_data["code"]:
            return Response(
                {"error_detail": "응시 코드가 일치하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 권한 확인 (수강생만)
        user = cast(User, request.user)
        if user.role != User.Role.STUDENT:
            return Response(
                {"error_detail": "시험에 응시할 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 시험 상태 확인
        if deployment.status != ExamDeployment.StatusChoices.ACTIVATED:
            return Response(
                {"error_detail": "현재 응시할 수 없는 시험입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 시험 시간 확인
        now = timezone.now()
        if now < deployment.open_at:
            return Response(
                {"error_detail": "아직 응시할 수 없습니다."},
                status=status.HTTP_423_LOCKED,
            )
        if now > deployment.close_at:
            return Response(
                {"error_detail": "시험이 이미 종료되었습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 검증 성공 - 204 No Content 반환
        return Response(status=status.HTTP_204_NO_CONTENT)
