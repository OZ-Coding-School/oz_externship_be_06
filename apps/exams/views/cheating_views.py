from typing import Any, cast

from django.core.cache import cache
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ExamStatus
from apps.exams.models import ExamDeployment
from apps.exams.permissions import IsStudentRole
from apps.exams.serializers.cheating_serializers import ExamCheatingResponseSerializer
from apps.exams.serializers.error_serializers import (
    ErrorDetailSerializer,
    ErrorResponseSerializer,
)
from apps.exams.services.exam_status_service import is_exam_active
from apps.users.models import User


class ExamCheatingUpdateAPIView(APIView):
    """부정행위 횟수를 증가시키고 종료 여부를 판단."""

    permission_classes = [IsAuthenticated, IsStudentRole]
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
            401: OpenApiResponse(ErrorDetailSerializer, description="인증 실패"),
            403: OpenApiResponse(ErrorDetailSerializer, description="권한 없음"),
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
            return Response({"error_detail": "해당 시험 정보를 찾을 수 없습니다."}, status=404)

        if not is_exam_active(deployment):
            return Response({"error_detail": "시험이 이미 종료되었습니다."}, status=410)

        cache_key = f"exam:cheating:{deployment.id}:{user.id}"
        current_count = cache.get(cache_key)
        if current_count is not None and current_count >= 3:
            return Response({"error_detail": "시험이 이미 종료되었습니다."}, status=410)

        ttl_seconds = max(1, deployment.duration_time * 60)
        if current_count is None:
            cache.set(cache_key, 1, timeout=ttl_seconds)
            cheating_count = 1
        else:
            cheating_count = cache.incr(cache_key)

        is_closed = cheating_count >= 3
        serializer = self.serializer_class(
            data={
                "cheating_count": cheating_count,
                "exam_status": (ExamStatus.CLOSED if is_closed else ExamStatus.ACTIVATED).value,
                "force_submit": is_closed,
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
