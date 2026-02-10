from typing import Any, NoReturn

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsAdminStaff
from apps.users.serializers.admin.admin_student_score_serializers import (
    AdminStudentScoreSerializer,
)
from apps.users.services.admin_student_score_service import (
    StudentNotFoundError,
    get_student_scores,
)


class AdminStudentScoreAPIView(APIView):
    """
    어드민용 학생 성적 관리 뷰
    """

    permission_classes = [IsAuthenticated, IsAdminStaff]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        """권한 및 인증 에러 커스텀 처리"""
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied(detail="권한이 없습니다.")

    @extend_schema(
        tags=["admin_accounts"],
        summary="학생별 과목 점수 조회 API",
        description="""
        관리자 권한을 가진 사용자가 특정 학생의 과목별 평균 점수를 조회합니다.
        해당 학생이 응시한 모든 시험의 과목별 평균치를 계산하여 반환합니다.
        """,
        parameters=[
            OpenApiParameter(
                name="student_id",
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
                description="조회할 학생의 고유 ID",
            ),
        ],
        responses={
            200: AdminStudentScoreSerializer(many=True),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="학생을 찾을 수 없습니다."),
        },
    )
    def get(self, request: Request, student_id: int, *args: Any, **kwargs: Any) -> Response:
        """
        특정 학생의 과목별 성적 리스트를 반환합니다.
        """
        try:
            # 서비스 레이어에서 list[dict[str, Any]] 형태의 데이터를 반환받음
            score_data = get_student_scores(student_id)
        except StudentNotFoundError:
            return Response(
                {"error_detail": "학생을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # mypy 에러 방지: many=True를 통해 리스트 데이터임을 명시
        # 시리얼라이저 제네릭이 Any이므로 타입 호환성 문제가 해결됨
        serializer = AdminStudentScoreSerializer(instance=score_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
