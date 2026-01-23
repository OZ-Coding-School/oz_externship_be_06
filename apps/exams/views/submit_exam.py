from __future__ import annotations

from typing import cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.serializers.submit_exam import SubmitExamRequestSerializer
from apps.exams.services.submit_exam import submit_exam
from apps.users.models import User


class SubmitExamAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = SubmitExamRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        answers = [dict(a) for a in data["answers"]]
        user = cast(User, request.user)
        submission = submit_exam(
            user=user,
            deployment_id=data["deployment_id"],
            started_at=data.get("started_at"),
            answers=answers,
        )

        return Response(
            {
                "submission_id": submission.id,
                "correct_answer_count": submission.correct_answer_count,
                "result_url": f"/api/v1/exams/submissions/{submission.id}/result",
            },
            status=status.HTTP_201_CREATED,
        )
