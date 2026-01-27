from __future__ import annotations

from typing import cast

from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.models import ExamDeployment, ExamSubmission
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.serializers.student.exam_status import ExamStatusResponseSerializer
from apps.users.models import User


class ExamStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["exams"],
        summary="시험 상태 조회 API",
        description="시험 응시 상태를 조회합니다.",
        responses={
            200: ExamStatusResponseSerializer,
            400: OpenApiResponse(ErrorResponseSerializer, description="유효하지 않은 시험 응시 세션"),
            401: OpenApiResponse(ErrorResponseSerializer, description="인증 실패"),
            404: OpenApiResponse(ErrorResponseSerializer, description="시험 정보 없음"),
        },
    )
    def get(self, request: Request, deployment_id: int) -> Response:
        try:
            deployment = ExamDeployment.objects.get(id=deployment_id)
        except ExamDeployment.DoesNotExist:
            return Response(
                {"error_detail": "해당 시험 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = cast(User, request.user)
        submission = ExamSubmission.objects.filter(
            submitter=user,
            deployment=deployment,
        ).first()

        if not submission:
            return Response(
                {"error_detail": "유효하지 않은 시험 응시 세션입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        closed = deployment.status != ExamDeployment.StatusChoices.ACTIVATED or now > deployment.close_at
        force_submit = closed

        return Response(
            ExamStatusResponseSerializer(
                {
                    "exam_status": "closed" if closed else "in_progress",
                    "force_submit": force_submit,
                }
            ).data,
            status=status.HTTP_200_OK,
        )
