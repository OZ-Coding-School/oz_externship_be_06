from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Course
from apps.courses.serializers.course_serializer import CourseListResponseSerializer


# 과정 리스트 조회
class CourseListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["courses"],
        summary="과정 리스트 조회 API",
        description="""
등록된 전체 과정 목록을 조회합니다.

## 인증
- 로그인한 사용자만 조회 가능합니다.
        """,
        responses={200: CourseListResponseSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        # Mock
        mock_data = [
            Course(
                id=1,
                name="초격차 백엔드 부트캠프",
                tag="BE",
                thumbnail_img_url="https://example.com/images/backend.png",
            ),
            Course(
                id=2,
                name="초격차 프론트엔드 부트캠프",
                tag="FE",
                thumbnail_img_url="https://example.com/images/frontend.png",
            ),
            Course(
                id=3,
                name="풀스택 개발자 과정",
                tag="FS",
                thumbnail_img_url="https://example.com/images/fullstack.png",
            ),
        ]
        serializer = CourseListResponseSerializer(mock_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
