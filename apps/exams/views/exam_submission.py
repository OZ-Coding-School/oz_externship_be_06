from django.contrib.auth.models import AnonymousUser
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.exams.models import ExamSubmission
from apps.exams.serializers import (
    ErrorDetailSerializer,
    ErrorResponseSerializer,
    ExamSubmissionCreateResponseSerializer,
    ExamSubmissionCreateSerializer,
)
from apps.exams.services.grading import grade_submission


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
        400: ErrorResponseSerializer,
        401: ErrorDetailSerializer,
        403: ErrorDetailSerializer,
        404: ErrorResponseSerializer,
        409: ErrorResponseSerializer,
    },
)
class ExamSubmissionCreateAPIView(APIView):
    # 인증과 권한 관리
    # 여기에서 401, 403 잡아주고 메세지는 자동으로 만들어줌
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]  # 로그인한 유저만 제출 가능

    def post(self, request: Request) -> Response:
        deployment_id = request.data.get("deployment_id")

        if not deployment_id:
            return Response(
                {"error_detail": "유효하지 않은 시험 응시 세션입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 응시한 submission 조회
        # 학생이 아직 시험을 시작하지 않았거나, 배포 ID가 잘못돼서 존재하지 않는 세션일 때
        try:
            submission = ExamSubmission.objects.get(
                submitter=request.user,  # type: ignore
                deployment_id=deployment_id,
            )
        except ExamSubmission.DoesNotExist:
            return Response(
                {"error_detail": "유효하지 않은 시험 응시 세션입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 409 이미 제출됨
        if submission.answers_json:
            return Response(
                {"error_detail": "이미 제출된 시험입니다."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = ExamSubmissionCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "submission": submission,
            },
        )

        serializer.is_valid(raise_exception=True)
        submission = serializer.save()

        # 채점 호출
        grade_submission(submission)
        submission.refresh_from_db()

        # 제출 성공 응답
        response_serializer = ExamSubmissionCreateResponseSerializer(
            {
                "submission_id": submission.id,
                "score": submission.score,
                "correct_answer_count": submission.correct_answer_count,
                "redirect_url": f"/api/v1/exams/submissions/{submission.id}",
            }
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
