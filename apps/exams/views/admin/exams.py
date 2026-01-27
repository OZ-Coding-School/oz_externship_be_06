from __future__ import annotations

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.permissions import IsExamStaff
from apps.exams.serializers.admin.exams import (
    AdminExamCreateRequestSerializer,
    AdminExamCreateResponseSerializer,
)
from apps.exams.serializers.error import ErrorDetailSerializer
from apps.exams.services.admin.exams import (
    ExamCreateConflictError,
    ExamCreateNotFoundError,
    create_exam,
)


class AdminExamCreateAPIView(APIView):
    """관리자 쪽지시험 생성 API."""

    permission_classes = [IsAuthenticated, IsExamStaff]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = AdminExamCreateRequestSerializer

    @extend_schema(
        tags=["admin_exams"],
        summary="관리자 쪽지시험 생성 API",
        description="""
        관리자/스태프 권한으로 쪽지시험을 생성합니다.
        """,
        request=AdminExamCreateRequestSerializer,
        responses={
            201: AdminExamCreateResponseSerializer,
            400: OpenApiResponse(ErrorDetailSerializer, description="유효하지 않은 시험 생성 요청"),
            401: OpenApiResponse(ErrorDetailSerializer, description="인증 실패"),
            403: OpenApiResponse(ErrorDetailSerializer, description="쪽지시험 생성 권한 없음"),
            404: OpenApiResponse(ErrorDetailSerializer, description="과목 정보 없음"),
            409: OpenApiResponse(ErrorDetailSerializer, description="동일한 이름의 시험 존재"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = AdminExamCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": "유효하지 않은 시험 생성 요청입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        try:
            exam = create_exam(
                title=data["title"],
                subject_id=data["subject_id"],
                thumbnail_img=data["thumbnail_img"],
            )
        except ExamCreateNotFoundError:
            return Response(
                {"error_detail": "해당 과목 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ExamCreateConflictError:
            return Response(
                {"error_detail": "동일한 이름의 시험이 이미 존재합니다."},
                status=status.HTTP_409_CONFLICT,
            )

        response_serializer = AdminExamCreateResponseSerializer(exam)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
