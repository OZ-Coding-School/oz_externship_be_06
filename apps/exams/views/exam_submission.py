from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.models import ExamDeployment
from apps.exams.serializers import (
    ExamSubmissionCreateResponseSerializer,
    ExamSubmissionCreateSerializer,
)
from apps.exams.services.grading import grade_submission


class ExamSubmissionCreateView(APIView):
    # 인증과 권한 관리
    # 여기에서 401, 403 잡아주고 메세지는 자동으로 만들어줌
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]  # 로그인한 유저만 제출 가능

    def post(self, request: Request) -> Response:
        deployment_id = request.data.get("deployment")
        deployment = get_object_or_404(
            ExamDeployment,
            id=deployment_id,
        )

        serializer = ExamSubmissionCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "deployment": deployment,
            },
        )

        try:
            serializer.is_valid(raise_exception=True)
            submission = serializer.save()
        except ValidationError as e:
            # 400 / 409 에러 처리
            msg = e.detail if isinstance(e.detail, str) else str(e.detail)
            if "이미 제출" in msg:
                return Response({"error_detail": msg}, status=status.HTTP_409_CONFLICT)
            return Response({"error_detail": msg}, status=status.HTTP_400_BAD_REQUEST)

        # 채점 호출
        grade_submission(submission)
        submission.refresh_from_db()

        # 제출 성공 응답
        response_data = {
            "submission_id": submission.id,
            "score": submission.score,
            "correct_answer_count": submission.correct_answer_count,
            "redirect_url": "/exam/result/",  # 필요에 맞게 변경
        }
        response_serializer = ExamSubmissionCreateResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
