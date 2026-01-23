from __future__ import annotations

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.models import ExamDeployment, ExamSubmission


class ExamStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, deployment_id: int) -> Response:
        try:
            deployment = ExamDeployment.objects.get(id=deployment_id)
        except ExamDeployment.DoesNotExist:
            return Response(
                {"error_detail": "해당 시험 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        submission = ExamSubmission.objects.filter(
            submitter=request.user,
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
            {
                "exam_status": "closed" if closed else "in_progress",
                "force_submit": force_submit,
            },
            status=status.HTTP_200_OK,
        )
