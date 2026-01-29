from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.serializers.admin.subject_serializers import SubjectScatterSerializer
from apps.courses.services.admin.subject_service import (
    AdminSubjectService,
    SubjectNotFoundError,
)
from apps.courses.utils.constants import ErrorMessages


class AdminSubjectScatterView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        tags=["admin_courses"],
        summary="과목별 학습시간/점수 산점도 조회",
        description="특정 과목의 학습시간과 점수 데이터를 산점도용으로 조회합니다.",
        responses={
            200: SubjectScatterSerializer(many=True),
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
                examples=[OpenApiExample("과목 없음", value={"error_detail": ErrorMessages.SUBJECT_NOT_FOUND.value})],
            ),
        },
    )
    def get(self, request: Request, subject_id: int) -> Response:
        subject = AdminSubjectService.validate_subject_exists(subject_id)
        scatter_data = AdminSubjectService.get_scatter_data(subject)
        serializer = SubjectScatterSerializer(scatter_data, many=True)
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
        if isinstance(exc, SubjectNotFoundError):
            return Response(
                {"error_detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )
        return super().handle_exception(exc)
