from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.serializers.admin.cohort_serializers import CohortAvgScoreSerializer
from apps.courses.services.admin.cohort_service import (
    AdminCohortService,
    CourseNotFoundError,
)
from apps.courses.utils.constants import ErrorMessages


class AdminCohortAvgScoresView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        tags=["admin_courses"],
        summary="기수별 평균 점수 조회",
        description="특정 과정의 기수별 평균 점수를 조회합니다.",
        responses={
            200: CohortAvgScoreSerializer(many=True),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[OpenApiExample("인증 실패", value={"error_detail": ErrorMessages.UNAUTHORIZED.value})],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                examples=[OpenApiExample("권한 없음", value={"error_detail": ErrorMessages.ADMIN_FORBIDDEN.value})],
            ),
            404: OpenApiResponse(
                description="Not Found",
                examples=[OpenApiExample("과정 없음", value={"error_detail": ErrorMessages.COURSE_NOT_FOUND.value})],
            ),
        },
    )
    def get(self, request: Request, course_id: int) -> Response:
        AdminCohortService.validate_course_exists(course_id)
        scores = AdminCohortService.get_cohort_avg_scores(course_id)
        serializer = CohortAvgScoreSerializer(scores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"error_detail": ErrorMessages.UNAUTHORIZED.value},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if isinstance(exc, PermissionDenied):
            return Response(
                {"error_detail": ErrorMessages.ADMIN_FORBIDDEN.value},
                status=status.HTTP_403_FORBIDDEN,
            )
        if isinstance(exc, CourseNotFoundError):
            return Response(
                {"error_detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )
        return super().handle_exception(exc)
