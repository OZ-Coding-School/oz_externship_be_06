from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.courses.serializers.admin.subject_serializers import (
    SubjectCreateRequestSerializer,
    SubjectCreateResponseSerializer,
)
from apps.courses.services.admin.subject_service import (
    AdminSubjectService,
    CourseNotFoundError,
    SubjectAlreadyExistsError,
)
from apps.courses.utils.constants import ErrorMessages


# 어드민 과목 생성 api
class AdminSubjectCreateView(APIView):

    permission_classes = [IsAuthenticated, IsStaffRole]

    @extend_schema(
        tags=["admin_courses"],
        summary="어드민 과목 생성",
        description="""새로운 과목을 생성합니다.
        url 빈값이어도 등록 가능 추후 presigned url 구현 후 필수 값으로 수정 예정입니다!""",
        request=SubjectCreateRequestSerializer,
        responses={
            201: OpenApiResponse(
                response=SubjectCreateResponseSerializer,
                description="Created",
                examples=[
                    OpenApiExample(
                        "성공",
                        value={
                            "id": 1,
                            "course_id": 1,
                            "title": "HTML",
                            "number_of_days": 5,
                            "number_of_hours": 40,
                            "thumbnail_img_url": "https://example.com/html.png",
                            "status": True,
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 요청",
                        value={"error_detail": ErrorMessages.INVALID_SUBJECT_CREATE.value},
                    )
                ],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        "인증 실패",
                        value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                    )
                ],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        "권한 없음",
                        value={"error_detail": ErrorMessages.SUBJECT_CREATE_FORBIDDEN.value},
                    )
                ],
            ),
            404: OpenApiResponse(
                description="Not Found",
                examples=[
                    OpenApiExample(
                        "과정 없음",
                        value={"error_detail": ErrorMessages.COURSE_NOT_FOUND.value},
                    )
                ],
            ),
            409: OpenApiResponse(
                description="Conflict",
                examples=[
                    OpenApiExample(
                        "중복 과목명",
                        value={"error_detail": ErrorMessages.SUBJECT_ALREADY_EXISTS.value},
                    )
                ],
            ),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = SubjectCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": ErrorMessages.INVALID_SUBJECT_CREATE.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            subject = AdminSubjectService.create_subject(serializer.validated_data)
        except CourseNotFoundError:
            return Response(
                {"error_detail": ErrorMessages.COURSE_NOT_FOUND.value},
                status=status.HTTP_404_NOT_FOUND,
            )
        except SubjectAlreadyExistsError:
            return Response(
                {"error_detail": ErrorMessages.SUBJECT_ALREADY_EXISTS.value},
                status=status.HTTP_409_CONFLICT,
            )

        response_serializer = SubjectCreateResponseSerializer(subject)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"error_detail": ErrorMessages.UNAUTHORIZED.value},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if isinstance(exc, PermissionDenied):
            return Response(
                {"error_detail": ErrorMessages.SUBJECT_CREATE_FORBIDDEN.value},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().handle_exception(exc)
