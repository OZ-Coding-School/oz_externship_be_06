from typing import NoReturn

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsAdminStaff
from apps.users.serializers.admin.admin_analytics_serializers import (
    SignupTrendsRequestSerializer,
    SignupTrendsResponseSerializer,
)
from apps.users.services.admin_analytics_service import get_signup_trends

#회원가입 추세 분석
class AdminSignupTrendsAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminStaff]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied(detail="권한이 없습니다.")

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 회원가입 추세 분석 API",
        description="""
        스태프(조교, 러닝코치, 운영매니저) 또는 관리자가 회원가입 추세를 조회합니다.

        - monthly: 특정 연도의 1~12월 회원가입 인원수 (year 파라미터로 연도 지정, 기본값: 현재 연도)
        - yearly: 전체 기간의 연도별 회원가입 인원수
        """,
        parameters=[
            OpenApiParameter(
                name="interval",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="조회 간격 (monthly: 월별, yearly: 년별)",
                enum=["monthly", "yearly"],
            ),
            OpenApiParameter(
                name="year",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="조회할 연도 (monthly인 경우에만 사용, 기본값: 현재 연도)",
            ),
        ],
        responses={
            200: SignupTrendsResponseSerializer,
            400: OpenApiResponse(description="잘못된 요청입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
        },
    )
    def get(self, request: Request) -> Response:
        serializer = SignupTrendsRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=400)

        interval = serializer.validated_data["interval"]
        year = serializer.validated_data.get("year")

        result = get_signup_trends(interval, year)

        response_serializer = SignupTrendsResponseSerializer(result)
        return Response(response_serializer.data, status=200)
