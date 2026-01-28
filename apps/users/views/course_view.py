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
from apps.users.services.course_service import (
    get_available_courses,
    get_enrolled_courses,
)


# 수강신청 가능한 기수 조회
class AvailableCoursesAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="수강신청 가능한 기수 조회 API",
        description="""
현재 수강신청이 가능한 기수 목록을 조회합니다.

## 조회 조건
- 모집 기간(`recruitment_start_date` ~ `recruitment_end_date`) 내에 있는 기수만 조회됩니다.
- 모집 상태가 활성화된 기수만 표시됩니다.
        """,
        responses={200: AvailableCourseResponseSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        courses = get_available_courses()
        serializer = AvailableCourseResponseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 내 수강목록 조회
class EnrolledCoursesAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="내 수강목록 조회 API",
        description="""
현재 로그인한 사용자가 수강 중이거나 수강 완료한 과정 목록을 조회합니다.

## 응답 필드
- `id`: 수강 기록 고유 ID
- `cohort_id`: 기수 ID
- `cohort_name`: 기수명
- `course_name`: 과정명
- `status`: 수강 상태 (진행중/완료/중단 등)
- `enrolled_at`: 수강 신청일
- `start_date`: 과정 시작일
- `end_date`: 과정 종료일

## 주의사항
- 수강생 권한(`STUDENT`)이 있는 사용자만 수강 목록이 표시됩니다.
- 일반 회원(`USER`)은 빈 배열이 반환됩니다.
        """,
        responses={200: EnrolledCourseResponseSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        courses = get_enrolled_courses(user=request.user)  # type: ignore[arg-type]
        serializer = EnrolledCourseResponseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
