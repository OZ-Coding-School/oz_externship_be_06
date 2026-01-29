from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.serializers.admin.subject_serializers import SubjectListSerializer
from apps.courses.services.admin.subject_service import SubjectListService
from apps.courses.utils.constants import ErrorMessages


class AdminSubjectListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        tags=["admin_courses"],
        summary="과목 목록 조회",
        description="특정 과정의 과목 목록을 조회합니다.",
        responses={
            200: SubjectListSerializer(many=True),
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
    def get(self, request: Request, course_id: int) -> Response:
        subjects = SubjectListService.get_subjects_by_course(course_id)
        serializer = SubjectListSerializer(subjects, many=True)
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
        return super().handle_exception(exc)
