from typing import NoReturn

from django.db.models import Q, QuerySet
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models.enrollment import StudentEnrollmentRequest
from apps.users.permissions import IsAdminStaff
from apps.users.serializers.admin.admin_student_enrollment_serializers import (
    AdminStudentEnrollmentListSerializer,
)
from apps.users.utils.pagination import AdminListPagination


class AdminStudentEnrollmentListAPIView(APIView):
    """어드민 수강생 등록 요청 목록 조회 API."""

    permission_classes = [IsAuthenticated, IsAdminStaff]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied(detail="권한이 없습니다.")

    @extend_schema(
        tags=["admin_students"],
        summary="어드민 페이지 수강생 등록 요청 목록 조회 API",
        description="""
        스태프(조교, 러닝코치, 운영매니저) 또는 관리자가 수강생 등록 요청 목록을 조회합니다.

        페이지네이션, 검색, 필터링, 정렬 기능을 제공합니다.
        기본적으로 ID 순으로 정렬됩니다.
        """,
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="페이지 번호",
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="페이지 크기 (기본: 10, 최대: 100)",
            ),
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="검색어 (이름, 이메일)",
            ),
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="상태 필터",
                enum=["pending", "accepted", "rejected"],
            ),
            OpenApiParameter(
                name="sort",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="정렬 기준 (id: ID순, latest: 최신순, oldest: 오래된순)",
                enum=["id", "latest", "oldest"],
            ),
        ],
        responses={
            200: AdminStudentEnrollmentListSerializer(many=True),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
        },
    )
    def get(self, request: Request) -> Response:
        queryset = self._get_queryset(request)

        # 페이지네이션 적용
        paginator = AdminListPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = AdminStudentEnrollmentListSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    def _get_queryset(self, request: Request) -> QuerySet[StudentEnrollmentRequest]:
        """필터링된 수강생 등록 요청 쿼리셋을 반환합니다."""
        queryset = StudentEnrollmentRequest.objects.select_related(
            "user", "cohort__course"
        )

        # 검색 필터
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(user__name__icontains=search) | Q(user__email__icontains=search)
            )

        # 상태 필터
        status_filter = request.query_params.get("status")
        if status_filter:
            # 명세서는 accepted, 모델은 APPROVED
            if status_filter == "accepted":
                queryset = queryset.filter(status=StudentEnrollmentRequest.Status.APPROVED)
            elif status_filter == "rejected":
                queryset = queryset.filter(status=StudentEnrollmentRequest.Status.REJECTED)
            elif status_filter == "pending":
                queryset = queryset.filter(status=StudentEnrollmentRequest.Status.PENDING)

        # 정렬
        sort = request.query_params.get("sort", "id")
        if sort == "latest":
            queryset = queryset.order_by("-created_at")
        elif sort == "oldest":
            queryset = queryset.order_by("created_at")
        else:
            queryset = queryset.order_by("id")

        return queryset
