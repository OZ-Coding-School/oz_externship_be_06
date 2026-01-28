from typing import NoReturn

from django.db.models import Q, QuerySet
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.permissions import IsAdminStaff
from apps.users.serializers.admin.admin_student_list_serializers import (
    AdminStudentListSerializer,
)
from apps.users.utils.pagination import AdminListPagination


# 어드민 수강생 목록 조회 api
class AdminStudentListAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminStaff]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied(detail="권한이 없습니다.")

    def get_queryset(self, request: Request) -> QuerySet[User]:
        queryset = (
            User.objects.filter(role=User.Role.STUDENT)
            .select_related()
            .prefetch_related("cohort_students__cohort__course")
        )

        # 검색 필터
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(email__icontains=search)
                | Q(nickname__icontains=search)
                | Q(phone_number__icontains=search)
            )

        # 상태 필터
        status_filter = request.query_params.get("status")
        if status_filter:
            status_map = {
                "activated": True,
                "deactivated": False,
            }
            if status_filter.lower() in status_map:
                queryset = queryset.filter(is_active=status_map[status_filter.lower()])
            elif status_filter.lower() == "withdrew":
                queryset = queryset.filter(withdrawal__isnull=False)

        # 과정 ID 필터
        course_id = request.query_params.get("course_id")
        if course_id:
            queryset = queryset.filter(cohort_students__cohort__course_id=course_id)

        # 기수 ID 필터
        cohort_id = request.query_params.get("cohort_id")
        if cohort_id:
            queryset = queryset.filter(cohort_students__cohort_id=cohort_id)

        return queryset.distinct().order_by("id")

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 수강생 목록 조회 API",
        description="""
        스태프(조교, 러닝코치, 운영매니저) 또는 관리자가 수강생 목록을 조회합니다.

        페이지네이션, 검색, 필터링 기능을 제공
        기본적으로 ID 순으로 정렬
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
                description="검색어 (이름, 이메일, 닉네임, 연락처)",
            ),
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="상태 필터 (activated, deactivated, withdrew)",
                enum=["activated", "deactivated", "withdrew"],
            ),
            OpenApiParameter(
                name="course_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="과정 ID 필터",
            ),
            OpenApiParameter(
                name="cohort_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="기수 ID 필터",
            ),
        ],
        responses={
            200: OpenApiResponse(description="수강생 목록"),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
        },
    )
    def get(self, request: Request) -> Response:
        queryset = self.get_queryset(request)

        paginator = AdminListPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = AdminStudentListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = AdminStudentListSerializer(queryset, many=True)
        return Response(serializer.data)
