from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.serializers.admin.cohort_serializers import (
    CohortCreateRequestSerializer,
)
from apps.courses.services.admin.cohort_service import AdminCohortService
from apps.courses.services.course_service import CourseNotFoundError
from apps.courses.utils.constants import ErrorMessages


class AdminCohortCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        tags=["admin_courses"],
        summary="기수 등록",
        description="새로운 기수를 등록합니다.",
        request=CohortCreateRequestSerializer,
        responses={
            201: OpenApiResponse(
                description="Created",
                examples=[OpenApiExample("성공", value={"detail": "기수가 등록되었습니다.", "id": 1})],
            ),
            400: OpenApiResponse(description="Bad Request"),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[OpenApiExample("인증 실패", value={"error_detail": ErrorMessages.UNAUTHORIZED.value})],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                examples=[OpenApiExample("권한 없음", value={"error_detail": ErrorMessages.ADMIN_FORBIDDEN.value})],
            ),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CohortCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cohort = AdminCohortService.create_cohort(serializer.validated_data)
        return Response(
            {"detail": "기수가 등록되었습니다.", "id": cohort.id},
            status=status.HTTP_201_CREATED,
        )

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
