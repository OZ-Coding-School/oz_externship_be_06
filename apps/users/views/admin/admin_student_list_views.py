from typing import Any, NoReturn

from django.db.models import Q, QuerySet
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
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


class AdminStudentListAPIView(APIView):
    """
    어드민용 사용자(수강생 및 스태프) 목록 조회 뷰
    """

    permission_classes = [IsAuthenticated, IsAdminStaff]
    pagination_class = AdminListPagination

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        """인증 및 권한 예외 커스텀 메시지 처리"""
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied(detail="권한이 없습니다.")

    def get_queryset(self, request: Request) -> QuerySet[User]:
        """쿼리 파라미터에 따른 필터링된 유저 쿼리셋 반환"""
        queryset = User.objects.all().prefetch_related("cohort_students__cohort__course")

        # 1. 역할(Role) 필터: 테스트 코드 대응 및 기본값 STUDENT 설정
        role_param = request.query_params.get("role")
        if role_param:
            queryset = queryset.filter(role=role_param.upper())
        else:
            queryset = queryset.filter(role=User.Role.STUDENT)

        # 2. 검색 필터
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(email__icontains=search)
                | Q(nickname__icontains=search)
                | Q(phone_number__icontains=search)
            )

        # 3. 상태(Status) 필터
        status_filter = request.query_params.get("status", "").lower()
        if status_filter in ["activated", "deactivated"]:
            queryset = queryset.filter(is_active=(status_filter == "activated"))
        elif status_filter == "withdrew":
            queryset = queryset.filter(withdrawal__isnull=False)

        # 4. 과정 및 기수 필터
        course_id = request.query_params.get("course_id")
        if course_id:
            queryset = queryset.filter(cohort_students__cohort__course_id=course_id)

        cohort_id = request.query_params.get("cohort_id")
        if cohort_id:
            queryset = queryset.filter(cohort_students__cohort_id=cohort_id)

        # [수정] 테스트 코드(test_ordered_by_id) 통과를 위해 id 순으로 정렬
        return queryset.distinct().order_by("id")

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 사용자 목록 조회 API",
        parameters=[
            OpenApiParameter(name="role", type=str, description="역할 필터 (STUDENT, TA, OM, LC 등)"),
            OpenApiParameter(name="search", type=str, description="검색어"),
            OpenApiParameter(name="status", type=str, enum=["activated", "deactivated", "withdrew"]),
            OpenApiParameter(name="course_id", type=int, description="과정 ID"),
            OpenApiParameter(name="cohort_id", type=int, description="기수 ID"),
        ],
        responses={200: AdminStudentListSerializer(many=True)},
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = self.get_queryset(request)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = AdminStudentListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = AdminStudentListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
