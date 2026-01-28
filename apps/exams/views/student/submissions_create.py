from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from typing import NoReturn

from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.exams.constants import ErrorMessages
from apps.exams.serializers import (
    ErrorResponseSerializer,
    ExamSubmissionCreateResponseSerializer,
    ExamSubmissionCreateSerializer,
)
from apps.exams.services.grading import grade_submission
from apps.exams.services.student.submissions_create import submit_exam


@extend_schema(
    tags=["Exams"],
    summary="쪽지시험 제출 API",
    description="""
    로그인한 사용자가 쪽지시험 답안을 제출합니다.
    제출 후 즉시 채점이 수행되며 점수와 정답 개수가 반환됩니다.
    """,
    request=ExamSubmissionCreateSerializer,
    responses={
        201: ExamSubmissionCreateResponseSerializer,
        400: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.INVALID_EXAM_SESSION.value),
        401: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.UNAUTHORIZED.value),
        403: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.FORBIDDEN.value),
        404: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.EXAM_NOT_FOUND.value),
        409: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.SUBMISSION_ALREADY_SUBMITTED.value),
    },
)
class ExamSubmissionCreateAPIView(APIView):
    # 인증과 권한 관리
    # 여기에서 401, 403 잡아주고 메세지는 자동으로 만들어줌
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail=ErrorMessages.UNAUTHORIZED.value)
        raise PermissionDenied(detail=ErrorMessages.FORBIDDEN.value)

    def post(self, request: Request) -> Response:
        serializer = ExamSubmissionCreateSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        submission = submit_exam(
            user=request.user,  # type: ignore
            deployment_id=serializer.validated_data["deployment_id"],
            started_at=serializer.validated_data["started_at"],
            cheating_count=serializer.validated_data["cheating_count"],
            answers=serializer.validated_data["answers"],
        )

        # 채점 호출
        grade_submission(submission)
        submission.refresh_from_db()

        # 제출 성공 응답
        response_serializer = ExamSubmissionCreateResponseSerializer(
            {
                "submission_id": submission.id,
                "score": submission.score,
                "correct_answer_count": submission.correct_answer_count,
                "redirect_url": f"/exam/result/{submission.id}",
            }
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
