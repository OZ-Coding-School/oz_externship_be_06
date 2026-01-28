from typing import NoReturn

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.permissions import IsExamStaff
from apps.exams.serializers.admin_submission_delete_serializers import (
    AdminExamSubmissionDeleteResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin_submission_delete_service import (
    ExamSubmissionDeleteConflictError,
    ExamSubmissionDeleteNotFoundError,
    delete_exam_submission,
)


class AdminExamSubmissionDeleteAPIView(APIView):
    """어드민 쪽지시험 응시내역 삭제 API."""

    permission_classes = [IsAuthenticated, IsExamStaff]
    serializer_class = AdminExamSubmissionDeleteResponseSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail="쪽지시험 응시 내역 삭제 권한이 없습니다.")

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        elif isinstance(exc, PermissionDenied):
            return Response(
                {"error_detail": "쪽지시험 응시 내역 삭제 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().handle_exception(exc)

    @extend_schema(
        tags=["admin_exams"],
        summary="어드민 쪽지시험 응시내역 삭제 API",
        description="""
        스태프/관리자가 쪽지시험 응시내역을 삭제합니다.
        """,
        parameters=[
            OpenApiParameter(
                name="submission_id",
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
                description="응시내역 ID",
            ),
        ],
        responses={
            200: AdminExamSubmissionDeleteResponseSerializer,
            400: OpenApiResponse(ErrorResponseSerializer, description="유효하지 않은 응시 내역 삭제 요청입니다."),
            401: OpenApiResponse(ErrorResponseSerializer, description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(ErrorResponseSerializer, description="쪽지시험 응시 내역 삭제 권한이 없습니다."),
            404: OpenApiResponse(ErrorResponseSerializer, description="삭제할 응시 내역을 찾을 수 없습니다."),
            409: OpenApiResponse(ErrorResponseSerializer, description="응시 내역 처리 중 충돌이 발생했습니다."),
        },
    )
    def delete(self, request: Request, submission_id: int) -> Response:
        if submission_id <= 0:
            return Response(
                {"error_detail": "유효하지 않은 응시 내역 삭제 요청입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            deleted_id = delete_exam_submission(submission_id)
        except ExamSubmissionDeleteNotFoundError:
            return Response(
                {"error_detail": "삭제할 응시 내역을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ExamSubmissionDeleteConflictError:
            return Response(
                {"error_detail": "응시 내역 처리 중 충돌이 발생했습니다."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = self.serializer_class(data={"submission_id": deleted_id})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
