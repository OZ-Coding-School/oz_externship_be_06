from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.permissions import IsExamStaff
from apps.exams.serializers.admin_question_serializers import (
    AdminExamQuestionCreateRequestSerializer,
    AdminExamQuestionCreateResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin_question_service import create_exam_question


class AdminExamQuestionCreateAPIView(APIView):
    """어드민 쪽지시험 문제 등록 API."""

    permission_classes = [IsAuthenticated, IsExamStaff]
    serializer_class = AdminExamQuestionCreateRequestSerializer

    @extend_schema(
        tags=["쪽지시험 관리"],
        summary="어드민 쪽지시험 문제 등록 API",
        description="""
        스태프(조교, 러닝 코치, 운영매니저), 관리자 권한을 가진 유저가
        쪽지시험 문제를 등록합니다.
        """,
        request=AdminExamQuestionCreateRequestSerializer,
        responses={
            201: AdminExamQuestionCreateResponseSerializer,
            400: OpenApiResponse(ErrorResponseSerializer, description="유효하지 않은 문제 등록 데이터"),
            401: OpenApiResponse(ErrorResponseSerializer, description="인증 실패"),
            403: OpenApiResponse(ErrorResponseSerializer, description="문제 등록 권한 없음"),
            404: OpenApiResponse(ErrorResponseSerializer, description="시험 정보 없음"),
            409: OpenApiResponse(ErrorResponseSerializer, description="문제 수/총점 초과"),
        },
    )
    def post(self, request: Request, exam_id: int) -> Response:
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({"error_detail": "유효하지 않은 문제 등록 데이터입니다."}, status=400)

        result = create_exam_question(exam_id, serializer.validated_data)
        if "error_detail" in result:
            status_code = 404 if result["error_detail"] == "해당 쪽지시험 정보를 찾을 수 없습니다." else 409
            return Response(result, status=status_code)

        response_serializer = AdminExamQuestionCreateResponseSerializer(data=result)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=201)
