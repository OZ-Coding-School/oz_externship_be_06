from django.core.cache import cache as django_cache
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsAdminStaff

ANALYTICS_CACHE_TTL = 3600  # 1시간
from apps.users.serializers.admin.admin_analytics_serializers import (
    AdminWithdrawalReasonCountsResponseSerializer,
    SignupTrendsRequestSerializer,
    SignupTrendsResponseSerializer,
    StudentEnrollmentTrendsRequestSerializer,
    StudentEnrollmentTrendsResponseSerializer,
    WithdrawalTrendsRequestSerializer,
    WithdrawalTrendsResponseSerializer,
)
from apps.users.services.admin_analytics_service import (
    get_signup_trends,
    get_student_enrollment_trends,
    get_withdrawal_reason_counts,
    get_withdrawal_trends,
)


# 어드민 분석 API의 공통 예외 처리를 담당하는 공통뷰
class AdminAnalyticsBaseAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminStaff]

    def handle_exception(self, exc: Exception) -> Response:
        response = super().handle_exception(exc)

        if isinstance(exc, (NotAuthenticated, PermissionDenied)) and response is not None:
            detail = response.data.get("detail")

            if isinstance(detail, dict) and "error_detail" in detail:
                message = detail["error_detail"]
            else:
                default_msg = (
                    "자격 인증 데이터가 제공되지 않았습니다."
                    if isinstance(exc, NotAuthenticated)
                    else "권한이 없습니다."
                )
                message = detail if isinstance(detail, str) else default_msg

            response.data = {"error_detail": message}

        return response


# 회원가입 추세 분석
class AdminSignupTrendsAPIView(AdminAnalyticsBaseAPIView):

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

        cache_key = f"signup_trends:{interval}:{year or 'all'}"
        data = django_cache.get(cache_key)

        if data is None:
            result = get_signup_trends(interval, year)
            data = SignupTrendsResponseSerializer(result).data
            django_cache.set(cache_key, data, timeout=ANALYTICS_CACHE_TTL)

        return Response(data, status=200)


# 회원 탈퇴 추세 분석 api
class AdminWithdrawalTrendsAPIView(AdminAnalyticsBaseAPIView):

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 회원탈퇴 추세 분석 API",
        description="""
        스태프(조교, 러닝코치, 운영매니저) 또는 관리자가 회원탈퇴 추세를 조회합니다.

        - monthly: 특정 연도의 1~12월 회원탈퇴 인원수 (현재 구현은 당해 연도 기준)
        - yearly: 전체 기간의 연도별 회원탈퇴 인원수
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
        ],
        responses={
            200: WithdrawalTrendsResponseSerializer,
            400: OpenApiResponse(description="잘못된 요청입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
        },
    )
    def get(self, request: Request) -> Response:
        serializer = WithdrawalTrendsRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({"error_detail": "잘못된 요청입니다."}, status=400)

        interval = serializer.validated_data["interval"]

        cache_key = f"withdrawal_trends:{interval}"
        data = django_cache.get(cache_key)

        if data is None:
            result = get_withdrawal_trends(interval)
            data = WithdrawalTrendsResponseSerializer(result).data
            django_cache.set(cache_key, data, timeout=ANALYTICS_CACHE_TTL)

        return Response(data, status=200)


# 수강등록 추세 분석 api
class AdminStudentEnrollmentTrendsAPIView(AdminAnalyticsBaseAPIView):

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 수강 등록 추세 분석 API",
        description="""
        스태프(조교, 러닝코치, 운영매니저) 또는 관리자가 수강 등록(수강생 전환) 추세를 조회합니다.

        - monthly: 특정 연도의 1~12월 수강 등록 인원수 (year 파라미터로 연도 지정, 기본값: 현재 연도)
        - yearly: 전체 기간의 연도별 수강 등록 인원수
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
            200: StudentEnrollmentTrendsResponseSerializer,
            400: OpenApiResponse(description="잘못된 요청입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
        },
    )
    def get(self, request: Request) -> Response:
        serializer = StudentEnrollmentTrendsRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({"error_detail": "잘못된 요청입니다."}, status=400)

        interval = serializer.validated_data["interval"]
        year = serializer.validated_data.get("year")

        cache_key = f"enrollment_trends:{interval}:{year or 'all'}"
        data = django_cache.get(cache_key)

        if data is None:
            result = get_student_enrollment_trends(interval, year)
            data = StudentEnrollmentTrendsResponseSerializer(result).data
            django_cache.set(cache_key, data, timeout=ANALYTICS_CACHE_TTL)

        return Response(data, status=200)


class AdminWithdrawalReasonCountsAPIView(AdminAnalyticsBaseAPIView):

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 전체 기간 회원 탈퇴 사유별 갯수 API",
        responses={200: AdminWithdrawalReasonCountsResponseSerializer},
    )
    def get(self, request: Request) -> Response:
        cache_key = "withdrawal_reason_counts"
        data = django_cache.get(cache_key)

        if data is None:
            result = get_withdrawal_reason_counts()
            data = AdminWithdrawalReasonCountsResponseSerializer(result).data
            django_cache.set(cache_key, data, timeout=ANALYTICS_CACHE_TTL)

        return Response(data, status=200)
