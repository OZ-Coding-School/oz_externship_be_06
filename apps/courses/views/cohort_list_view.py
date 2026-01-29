from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.serializers.cohort_serializers import CohortListSerializer
from apps.courses.services.cohort_service import CohortService
from apps.courses.utils.constants import ErrorMessages


class CohortListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["courses"],
        summary="기수 리스트 조회",
        description="특정 과정의 기수 목록을 조회합니다.",
        responses={
            200: CohortListSerializer(many=True),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[OpenApiExample("인증 실패", value={"error_detail": ErrorMessages.UNAUTHORIZED.value})],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                examples=[OpenApiExample("권한 없음", value={"error_detail": ErrorMessages.FORBIDDEN.value})],
            ),
        },
    )
    def get(self, request: Request, course_id: int) -> Response:
        cohorts = CohortService.get_cohorts_by_course(course_id)
        serializer = CohortListSerializer(cohorts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"error_detail": ErrorMessages.UNAUTHORIZED.value},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if isinstance(exc, PermissionDenied):
            return Response(
                {"error_detail": ErrorMessages.FORBIDDEN.value},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().handle_exception(exc)
