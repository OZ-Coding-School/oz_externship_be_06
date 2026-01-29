from typing import NoReturn

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, NotFound, PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam
from apps.exams.permissions import IsExamStaff
from apps.exams.serializers import (
    AdminExamUpdateRequestSerializer,
    AdminExamUpdateResponseSerializer,
    ErrorResponseSerializer,
)
from apps.exams.services.admin.exams_update import update_exam


@extend_schema(
    tags=["Admin Exams"],
    summary="쪽지시험 수정 API",
    description="스태프/관리자 권한을 가진 사용자가 쪽지시험 정보를 수정합니다.",
    request=AdminExamUpdateRequestSerializer,
    responses={
        200: AdminExamUpdateResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="유효하지 않은 요청",
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="인증 실패",
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="수정 권한 없음",
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="시험 정보 없음",
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="제목 중복",
        ),
    },
)
class AdminExamUpdateAPIView(APIView):
    permission_classes = [IsExamStaff]  # 스태프/관리자 권한 (403 권한 체크)

    # 401/403
    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail=ErrorMessages.UNAUTHORIZED.value)
        raise PermissionDenied(detail=ErrorMessages.NO_EXAM_UPDATE_PERMISSION.value)

    def put(self, request: Request, exam_id: int) -> Response:
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            raise NotFound(ErrorMessages.EXAM_UPDATE_NOT_FOUND.value)

        # 400/409 Serializer 검증
        serializer = AdminExamUpdateRequestSerializer(instance=exam, data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # 404 Service 호출
        exam = update_exam(
            exam_id=exam_id,
            title=validated_data.get("title"),
            subject=validated_data.get("subject"),
            thumbnail_img_url=validated_data.get("thumbnail_img"),
        )

        response_serializer = AdminExamUpdateResponseSerializer(exam)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
