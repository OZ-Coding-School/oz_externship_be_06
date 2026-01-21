from typing import Any, cast

from django.db import transaction
from django.db.models import F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ExamStatus
from apps.exams.models import ExamDeployment, ExamSubmission
from apps.exams.serializers.cheating_serializers import ExamCheatingResponseSerializer
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.exam_status_service import ensure_student_role, is_exam_closed
from apps.users.models import User


class ExamCheatingUpdateAPIView(APIView):
    """부정행위 횟수를 증가시키고 종료 여부를 판단."""

    permission_classes = [IsAuthenticated]
    serializer_class = ExamCheatingResponseSerializer

    @extend_schema(
        tags=["쪽지시험"],
        summary="쪽지시험 부정행위 카운트 업데이트 API",
        description="""
        시험 응시 중 화면 이탈 등 부정행위가 발생했을 때 카운트를 증가시킵니다.
        부정행위 3회 이상이면 force_submit=True로 종료 처리 응답을 반환합니다.
        """,
        parameters=[
            OpenApiParameter(
                name="deployment_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description="시험 배포 ID",
            )
        ],
        responses={
            200: ExamCheatingResponseSerializer,
            400: OpenApiResponse(ErrorResponseSerializer, description="유효하지 않은 시험 응시 세션"),
            401: OpenApiResponse(ErrorResponseSerializer, description="인증 실패"),
            403: OpenApiResponse(ErrorResponseSerializer, description="권한 없음"),
            404: OpenApiResponse(ErrorResponseSerializer, description="시험 정보 없음"),
            410: OpenApiResponse(ErrorResponseSerializer, description="시험 종료"),
        },
    )
    def post(self, request: Request, deployment_id: int) -> Response:
        user = cast(User, request.user)

        try:
            deployment_model = cast(Any, ExamDeployment)
            deployment = deployment_model.objects.select_related("exam", "cohort").get(id=deployment_id)
        except ExamDeployment.DoesNotExist:
            error = ErrorResponseSerializer(data={"error_detail": "해당 시험 정보를 찾을 수 없습니다."})
            error.is_valid(raise_exception=True)
            return Response(error.data, status=404)

        if not ensure_student_role(user):
            error = ErrorResponseSerializer(data={"error_detail": "권한이 없습니다."})
            error.is_valid(raise_exception=True)
            return Response(error.data, status=403)

        with transaction.atomic():
            submission_model = cast(Any, ExamSubmission)
            locked_submission = (
                submission_model.objects.select_for_update()
                .filter(submitter=user, deployment=deployment)
                .order_by("-created_at")
                .first()
            )
            if not locked_submission:
                error = ErrorResponseSerializer(data={"error_detail": "유효하지 않은 시험 응시 세션입니다."})
                error.is_valid(raise_exception=True)
                return Response(error.data, status=400)

            if is_exam_closed(deployment, locked_submission):
                error = ErrorResponseSerializer(data={"error_detail": "시험이 이미 종료되었습니다."})
                error.is_valid(raise_exception=True)
                return Response(error.data, status=410)

            locked_submission.cheating_count = F("cheating_count") + 1
            locked_submission.save(update_fields=["cheating_count", "updated_at"])
            locked_submission.refresh_from_db(fields=["cheating_count"])

        is_closed = is_exam_closed(deployment, locked_submission)
        serializer = self.serializer_class(
            data={
                "cheating_count": locked_submission.cheating_count,
                "exam_status": (ExamStatus.CLOSED if is_closed else ExamStatus.ACTIVATED).value,
                "force_submit": is_closed,
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
