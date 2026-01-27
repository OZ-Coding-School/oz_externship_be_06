from __future__ import annotations

from typing import cast

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.serializers.student.submit_exam import (
    SubmitExamRequestSerializer,
    SubmitExamResponseSerializer,
)
from apps.exams.services.student.submit_exam import submit_exam
from apps.users.models import User


class SubmitExamAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["exams"],
        summary="시험 제출 API",
        description="시험 답안을 제출합니다.",
        request=SubmitExamRequestSerializer,
        responses={
            201: SubmitExamResponseSerializer,
            400: OpenApiResponse(ErrorResponseSerializer, description="유효하지 않은 요청 또는 이미 제출된 시험"),
            401: OpenApiResponse(ErrorResponseSerializer, description="인증 실패"),
            403: OpenApiResponse(ErrorResponseSerializer, description="제출 권한 없음"),
            404: OpenApiResponse(ErrorResponseSerializer, description="시험 정보 없음"),
        },
    )
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
            SubmitExamResponseSerializer(
                {
                    "submission_id": submission.id,
                    "correct_answer_count": submission.correct_answer_count,
                    "score": submission.score,
                    "redirect_url": f"/api/v1/exams/submissions/{submission.id}/result",
                }
            ).data,
            status=status.HTTP_201_CREATED,
        )
