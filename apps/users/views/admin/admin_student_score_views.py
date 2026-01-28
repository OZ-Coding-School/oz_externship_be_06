from typing import Any, NoReturn

from django.db.models import Avg
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.models.exam_submissions import ExamSubmission
from apps.users.models import User
from apps.users.permissions import IsAdminStaff


# 학생별 과목 점수 조회 api
class AdminStudentScoreAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminStaff]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied(detail="권한이 없습니다.")

    @extend_schema(
        tags=["admin_accounts"],
        summary="학생별 과목 점수 조회 API",
        description="""
        스태프(조교, 러닝코치, 운영매니저) 또는 관리자가 학생의 과목별 점수를 조회합니다.

        각 과목별로 응시한 시험들의 평균 점수를 반환합니다.
        """,
        parameters=[
            OpenApiParameter(
                name="student_id",
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
                description="학생 ID",
            ),
        ],
        responses={
            200: OpenApiResponse(description="과목별 점수 목록"),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="학생을 찾을 수 없습니다."),
        },
    )
    def get(self, request: Request, student_id: int) -> Response:
        # 학생 조회
        try:
            student = User.objects.get(id=student_id, role=User.Role.STUDENT)
        except User.DoesNotExist:
            return Response(
                {"error_detail": "학생을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 과목별 평균 점수 조회
        scores = (
            ExamSubmission.objects.filter(submitter=student)
            .select_related("deployment__exam__subject")
            .values("deployment__exam__subject__title")
            .annotate(avg_score=Avg("score"))
            .order_by("deployment__exam__subject__title")
        )

        # 응답 형식에 맞게 변환
        result: list[dict[str, Any]] = [
            {
                "subject": score["deployment__exam__subject__title"],
                "score": round(score["avg_score"]) if score["avg_score"] else 0,
            }
            for score in scores
        ]

        return Response(result, status=status.HTTP_200_OK)
