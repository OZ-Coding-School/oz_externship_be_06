from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.permissions import IsExamQuestionDeleteStaff
from apps.exams.serializers.admin_question_delete_serializers import (
    AdminExamQuestionDeleteResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin_question_delete_service import (
    ExamQuestionDeleteConflictError,
    ExamQuestionDeleteNotFoundError,
    delete_exam_question,
)


class AdminExamQuestionDeleteAPIView(APIView):
    """어드민 쪽지시험 문제 삭제 API."""

    permission_classes = [IsAuthenticated, IsExamQuestionDeleteStaff]
    serializer_class = AdminExamQuestionDeleteResponseSerializer

    @extend_schema(
        tags=["관리자-쪽지시험"],
        summary="어드민 쪽지시험 문제 삭제 API",
        description="""
        스태프/관리자가 쪽지시험 문제를 삭제합니다.
        """,
        parameters=[
            OpenApiParameter(
                name="exam_id",
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
                description="쪽지시험 ID",
            ),
            OpenApiParameter(
                name="question_id",
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
                description="문제 ID",
            ),
        ],
        responses={
            200: AdminExamQuestionDeleteResponseSerializer,
            400: OpenApiResponse(ErrorResponseSerializer, description="유효하지 않은 요청"),
            401: OpenApiResponse(ErrorResponseSerializer, description="인증 실패"),
            403: OpenApiResponse(ErrorResponseSerializer, description="문제 삭제 권한 없음"),
            404: OpenApiResponse(ErrorResponseSerializer, description="문제 정보 없음"),
            409: OpenApiResponse(ErrorResponseSerializer, description="삭제 충돌"),
        },
    )
    def delete(self, request: Request, exam_id: int, question_id: int) -> Response:
        if exam_id <= 0 or question_id <= 0:
            return Response(
                {"error_detail": "유효하지 않은 문제 삭제 요청입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = delete_exam_question(exam_id, question_id)
        except ExamQuestionDeleteNotFoundError:
            return Response(
                {"error_detail": "삭제할 문제 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ExamQuestionDeleteConflictError:
            return Response(
                {"error_detail": "쪽지시험 문제 삭제 처리 중 충돌이 발생했습니다."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = self.serializer_class(data=result)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
