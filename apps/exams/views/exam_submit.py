from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from apps.exams.models import ExamDeployment, ExamSubmission
from apps.exams.serializers import ExamSubmitSerializer
from apps.exams.services.grading import grade_submission

User = get_user_model()

class ExamSubmitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, deployment_id: int) -> Response:
        deployment = get_object_or_404(ExamDeployment, id=deployment_id)

        serializer = ExamSubmitSerializer(
            data=request.data,
            context={"deployment": deployment},
        )
        serializer.is_valid(raise_exception=True)

        if not isinstance(request.user, User):
            raise PermissionDenied("로그인 필요")

        submission = ExamSubmission.objects.create(
            submitter=request.user,
            deployment=deployment,
            started_at=timezone.now(),
            answers_json=serializer.validated_data["answers"],
        )

        grade_submission(submission)
        submission.save()

        return Response(
            {
                "score": submission.score,
                "correct_answer_count": submission.correct_answer_count,
            }
        )
