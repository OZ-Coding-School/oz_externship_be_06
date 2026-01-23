from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.permissions import IsExamDeleteStaff
from apps.exams.serializers.admin_exam_delete_serializers import (
    AdminExamDeleteResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin_exam_delete_service import (
    ExamDeleteConflictError,
    ExamDeleteNotFoundError,
    delete_exam,
)


class AdminExamDeleteAPIView(APIView):
    """어드민 쪽지시험 삭제 API."""

    permission_classes = [IsAuthenticated, IsExamDeleteStaff]
    serializer_class = AdminExamDeleteResponseSerializer

    @extend_schema(
        tags=["관리자-쪽지시험"],
        summary="어드민 쪽지시험 삭제 API",
        description="""
        스태프/관리자가 쪽지시험을 삭제합니다.
        삭제 시 등록된 문제들도 함께 제거됩니다.
        """,
        responses={
            201: AdminExamDeleteResponseSerializer,
            400: OpenApiResponse(ErrorResponseSerializer, description="유효하지 않은 요청"),
            401: OpenApiResponse(ErrorResponseSerializer, description="인증 실패"),
            403: OpenApiResponse(ErrorResponseSerializer, description="삭제 권한 없음"),
            404: OpenApiResponse(ErrorResponseSerializer, description="시험 정보 없음"),
            409: OpenApiResponse(ErrorResponseSerializer, description="삭제 충돌"),
        },
    )
    def delete(self, request: Request, exam_id: int) -> Response:
        if exam_id <= 0:
            return Response(
                {"error_detail": "유효하지 않은 요청입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            deleted_id = delete_exam(exam_id)
        except ExamDeleteNotFoundError:
            return Response(
                {"error_detail": "삭제하려는 쪽지시험 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ExamDeleteConflictError:
            return Response(
                {"error_detail": "쪽지시험 삭제 중 충돌이 발생했습니다."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = self.serializer_class(data={"id": deleted_id})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
