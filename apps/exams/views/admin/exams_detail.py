from typing import NoReturn

from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import Exam, ExamQuestion
from apps.exams.serializers.admin.exams_delete import AdminExamDeleteResponseSerializer
from apps.exams.serializers.admin.exams_detail import AdminExamDetailSerializer
from apps.exams.serializers.admin.exams_update import (
    AdminExamUpdateRequestSerializer,
    AdminExamUpdateResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin.exams_delete import delete_exam
from apps.exams.services.admin.exams_detail import get_exam_detail_or_error
from apps.exams.services.admin.exams_update import update_exam
from apps.exams.views.mixins import ExamsExceptionMixin


class AdminExamDetailAPIView(ExamsExceptionMixin, APIView):
    """단일 Exam 리소스 조회/수정/삭제 API (단일 URL + HTTP 메소드 분리)"""

    permission_classes = [IsAuthenticated, IsStaffRole]

    # 401/403
    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail=ErrorMessages.UNAUTHORIZED.value)

        if request.method == "PUT":
            raise PermissionDenied(detail=ErrorMessages.NO_EXAM_UPDATE_PERMISSION.value)
        elif request.method == "DELETE":
            raise PermissionDenied(detail=ErrorMessages.NO_EXAM_DELETE_PERMISSION.value)
        elif request.method == "GET":
            raise PermissionDenied(detail=ErrorMessages.NO_EXAM_LIST_PERMISSION.value)
        else:
            raise PermissionDenied()

    @extend_schema(
        tags=["admin_exams"],
        summary="쪽지시험 상세 조회 API",
        description="스태프/관리자 권한을 가진 사용자가 단일 시험 상세 정보를 조회합니다.",
        responses={
            200: AdminExamDetailSerializer,
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 요청",
                        value={"error_detail": ErrorMessages.INVALID_EXAM_LIST_REQUEST.value},
                    )
                ],
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        "인증 실패",
                        value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                    )
                ],
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        "권한 없음",
                        value={"error_detail": ErrorMessages.NO_EXAM_LIST_PERMISSION.value},
                    )
                ],
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Not Found",
                examples=[
                    OpenApiExample(
                        "쪽지시험 정보 없음",
                        value={"error_detail": ErrorMessages.EXAM_NOT_FOUND.value},
                    )
                ],
            ),
        },
    )
    def get(self, request: Request, exam_id: int) -> Response:
        exam = get_exam_detail_or_error(exam_id=exam_id)
        serializer = AdminExamDetailSerializer(exam)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PUT → 수정
    @extend_schema(
        tags=["admin_exams"],
        summary="쪽지시험 수정 API",
        description="스태프/관리자 권한을 가진 사용자가 쪽지시험 정보를 수정합니다.",
        request=AdminExamUpdateRequestSerializer,
        responses={
            200: AdminExamUpdateResponseSerializer,
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 요청",
                        value={"error_detail": ErrorMessages.INVALID_EXAM_UPDATE_REQUEST.value},
                    )
                ],
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        "인증 실패",
                        value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                    )
                ],
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        "권한 없음",
                        value={"error_detail": ErrorMessages.NO_EXAM_UPDATE_PERMISSION.value},
                    )
                ],
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Not Found",
                examples=[
                    OpenApiExample(
                        "쪽지시험 정보 없음",
                        value={"error_detail": ErrorMessages.EXAM_UPDATE_NOT_FOUND.value},
                    )
                ],
            ),
            409: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Conflict",
                examples=[
                    OpenApiExample(
                        "시험 이름 중복",
                        value={"error_detail": ErrorMessages.EXAM_UPDATE_CONFLICT.value},
                    )
                ],
            ),
        },
    )
    def put(self, request: Request, exam_id: int) -> Response:
        serializer = AdminExamUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            raise ErrorDetailException(
                ErrorMessages.INVALID_EXAM_UPDATE_REQUEST.value,
                status.HTTP_400_BAD_REQUEST,
            )

        exam = update_exam(
            exam_id=exam_id,
            **serializer.validated_data,
        )

        response_serializer = AdminExamUpdateResponseSerializer(exam)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # DELETE → 삭제
    @extend_schema(
        tags=["admin_exams"],
        summary="쪽지시험 삭제 API",
        description="스태프/관리자 권한을 가진 사용자가 단일 시험을 삭제합니다.",
        responses={
            200: AdminExamDeleteResponseSerializer,
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 요청",
                        value={"error_detail": ErrorMessages.INVALID_EXAM_DELETE_REQUEST.value},
                    ),
                ],
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        "인증 실패",
                        value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                    ),
                ],
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        "권한 없음",
                        value={"error_detail": ErrorMessages.NO_EXAM_DELETE_PERMISSION.value},
                    ),
                ],
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Not Found",
                examples=[
                    OpenApiExample(
                        "시험 정보 없음",
                        value={"error_detail": ErrorMessages.EXAM_DELETE_NOT_FOUND.value},
                    ),
                ],
            ),
            409: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Conflict",
                examples=[
                    OpenApiExample(
                        "삭제 충돌",
                        value={"error_detail": ErrorMessages.EXAM_DELETE_CONFLICT.value},
                    ),
                ],
            ),
        },
    )
    def delete(self, request: Request, exam_id: int) -> Response:
        if exam_id <= 0:
            raise_error(ErrorMessages.INVALID_EXAM_DELETE_REQUEST)

        deleted_id = delete_exam(exam_id)

        serializer = AdminExamDeleteResponseSerializer({"id": deleted_id})
        return Response(serializer.data, status=status.HTTP_200_OK)
