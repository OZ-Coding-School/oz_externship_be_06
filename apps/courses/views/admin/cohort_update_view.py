from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.serializers.admin.cohort_serializers import (
    CohortUpdateRequestSerializer,
    CohortUpdateResponseSerializer,
)
from apps.courses.services.admin.cohort_service import (
    AdminCohortService,
    CohortNotFoundError,
)
from apps.courses.utils.constants import ErrorMessages


class AdminCohortUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        tags=["admin_courses"],
        summary="기수 정보 수정",
        description="기수 정보를 수정합니다.",
        request=CohortUpdateRequestSerializer,
        responses={
            200: CohortUpdateResponseSerializer,
            400: OpenApiResponse(description="Bad Request"),
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
                examples=[OpenApiExample("기수 없음", value={"error_detail": ErrorMessages.COHORT_NOT_FOUND.value})],
            ),
        },
    )
    def patch(self, request: Request, cohort_id: int) -> Response:
        cohort = AdminCohortService.get_cohort(cohort_id)

        serializer = CohortUpdateRequestSerializer(instance=cohort, data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_cohort = AdminCohortService.update_cohort(cohort, serializer.validated_data)
        response_serializer = CohortUpdateResponseSerializer(updated_cohort)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

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
        if isinstance(exc, CohortNotFoundError):
            return Response(
                {"error_detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )
        return super().handle_exception(exc)
