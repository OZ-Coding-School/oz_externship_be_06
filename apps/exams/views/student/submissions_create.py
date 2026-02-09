from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.exams.schemas.student import exam_submission_create_schema
from apps.exams.serializers import (
    ExamSubmissionCreateResponseSerializer,
    ExamSubmissionCreateSerializer,
)
from apps.exams.services.grading import grade_submission
from apps.exams.services.student.submissions_create import submit_exam
from apps.exams.views.mixins import ExamsExceptionMixin


# 쪽지시험 제출 API
@exam_submission_create_schema
class ExamSubmissionCreateAPIView(ExamsExceptionMixin, APIView):
    # 인증과 권한 관리
    # 여기에서 401, 403 잡아주고 메세지는 자동으로 만들어줌
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

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
