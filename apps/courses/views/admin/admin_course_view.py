from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.courses.serializers.admin.admin_course_serializer import (
    CourseCreateRequestSerializer,
    CourseCreateResponseSerializer,
    CourseUpdateRequestSerializer,
    CourseUpdateResponseSerializer,
)
from apps.courses.services.course_service import (
    CourseHasStudentsError,
    CourseNotFoundError,
    create_course,
    delete_course,
    update_course,
)


# 어드민 과정 등록
class AdminCourseCreateAPIView(APIView):

    permission_classes = [IsAuthenticated, IsStaffRole]

    @extend_schema(
        tags=["admin_courses"],
        summary="어드민 페이지 과정 등록 API",
        description="""
새로운 과정을 등록합니다.

## 권한
- 스태프(조교, 러닝코치, 운영매니저) 또는 관리자만 접근 가능
        """,
        request=CourseCreateRequestSerializer,
        responses={
            201: CourseCreateResponseSerializer,
            400: OpenApiResponse(description="유효성 검사 실패"),
            401: OpenApiResponse(description="인증 실패"),
            403: OpenApiResponse(description="권한 없음"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CourseCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = create_course(validated_data=serializer.validated_data)

        response_serializer = CourseCreateResponseSerializer({"detail": "과정이 등록되었습니다.", "id": course.id})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# 어드민 과정 수정
class AdminCourseUpdateAPIView(APIView):

    permission_classes = [IsAuthenticated, IsStaffRole]

    @extend_schema(
        tags=["admin_courses"],
        summary="어드민 페이지 과정 정보 수정 API",
        description="""
등록된 과정의 정보를 수정합니다.

## 권한
- 스태프(조교, 러닝코치, 운영매니저) 또는 관리자만 접근 가능

## 수정 가능한 항목
- `name`: 과정명 (최대 30자)
- `tag`: 과정 태그 (최대 3자)
- `description`: 과정 소개 (최대 255자)
- `thumbnail_img_url`: 과정 썸네일 이미지 URL
        """,
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=int,
                location=OpenApiParameter.PATH,
                description="수정할 과정의 ID",
            ),
        ],
        request=CourseUpdateRequestSerializer,
        responses={
            200: CourseUpdateResponseSerializer,
            400: OpenApiResponse(description="유효성 검사 실패"),
            401: OpenApiResponse(description="인증 실패"),
            403: OpenApiResponse(description="권한 없음"),
            404: OpenApiResponse(description="과정을 찾을 수 없습니다."),
        },
    )
    def patch(self, request: Request, course_id: int) -> Response:
        serializer = CourseUpdateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            course = update_course(course_id=course_id, validated_data=serializer.validated_data)
        except CourseNotFoundError as e:
            return Response(
                {"error_detail": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = CourseUpdateResponseSerializer(course)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["admin_courses"],
        summary="어드민 페이지 과정 삭제 API",
        description="""
등록된 과정을 삭제합니다.

## 권한
- 스태프(조교, 러닝코치, 운영매니저) 또는 관리자만 접근 가능

## 삭제 조건
- 해당 과정에 등록된 수강생이 없어야 삭제 가능
- 과정 삭제 시 연결된 기수(Cohort)도 함께 삭제됨
        """,
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=int,
                location=OpenApiParameter.PATH,
                description="삭제할 과정의 ID",
            ),
        ],
        responses={
            204: OpenApiResponse(description="과정 삭제 성공"),
            400: OpenApiResponse(description="등록된 수강생이 있어 삭제 불가"),
            401: OpenApiResponse(description="인증 실패"),
            403: OpenApiResponse(description="권한 없음"),
            404: OpenApiResponse(description="과정을 찾을 수 없습니다."),
        },
    )
    def delete(self, request: Request, course_id: int) -> Response:
        try:
            delete_course(course_id=course_id)
        except CourseNotFoundError as e:
            return Response(
                {"error_detail": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except CourseHasStudentsError as e:
            return Response(
                {"error_detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
