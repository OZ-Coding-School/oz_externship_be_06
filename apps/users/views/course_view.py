from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.course_serializer import (
    AvailableCourseResponseSerializer,
    EnrolledCourseResponseSerializer,
)
from apps.users.services.course_service import get_available_courses, get_enrolled_courses

#수강신청 가능한 기수 조회
class AvailableCoursesAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="수강신청 가능한 기수 조회 API",
        description="현재 모집중인 기수 목록을 조회합니다.",
        responses={200: AvailableCourseResponseSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        courses = get_available_courses()
        serializer = AvailableCourseResponseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#내 수강목록 조회
class EnrolledCoursesAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="내 수강목록 조회 API",
        description="현재 로그인한 사용자의 수강목록을 조회합니다.",
        responses={200: EnrolledCourseResponseSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        courses = get_enrolled_courses(user=request.user)  # type: ignore[arg-type]
        serializer = EnrolledCourseResponseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
