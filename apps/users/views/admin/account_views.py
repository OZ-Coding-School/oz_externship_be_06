from typing import Any

from django.db.models import Q
from django.db.models.query import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from apps.users.models import User
from apps.users.serializers.admin.account_serializers import AdminAccountListSerializer


class AdminAccountPagination(PageNumberPagination):
    """
    명세서의 page_size 대응을 위한 커스텀 페이지네이션
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class AdminUserListView(generics.ListAPIView[Any]):  # Generic 타입 힌트 [User]는 생략 가능
    """
    GET api/v1/admin/accounts
    어드민 페이지 회원 목록 조회 API
    """

    permission_classes = [permissions.IsAdminUser]
    serializer_class = AdminAccountListSerializer
    pagination_class = AdminAccountPagination

    def get_queryset(self) -> QuerySet[User]:
        # ✅ 피드백 반영: select_related("withdrawal")를 추가하여 N+1 문제 해결
        # User를 가져올 때 Withdrawal 정보를 JOIN으로 한 번에 가져옵니다.
        queryset = User.objects.select_related("withdrawal").all().order_by("-created_at")

        # 쿼리 파라미터 추출
        search = self.request.query_params.get("search")
        status_param = self.request.query_params.get("status")
        role_param = self.request.query_params.get("role")

        # 1. 검색 필터
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) | Q(nickname__icontains=search) | Q(name__icontains=search)
            )

        # 2. 상태 필터 (active, inactive, withdrew)
        if status_param:
            if status_param == "active":
                # withdrawal 정보가 없는(null) 활성 유저
                queryset = queryset.filter(is_active=True, withdrawal__isnull=True)
            elif status_param == "inactive":
                # 이메일 인증 전이거나 차단된 유저
                queryset = queryset.filter(is_active=False)
            elif status_param == "withdrew":
                # withdrawal 레코드가 존재하는 탈퇴 유저
                queryset = queryset.filter(withdrawal__isnull=False)

        # 3. 역할 필터
        if role_param:
            role_map = {"admin": "ADMIN", "staff": ["TA", "OM", "LC"], "user": "USER", "student": "STUDENT"}
            target_role = role_map.get(role_param.lower())
            if isinstance(target_role, list):
                queryset = queryset.filter(role__in=target_role)
            elif target_role:
                queryset = queryset.filter(role=target_role)

        return queryset

    @extend_schema(
        tags=["Admin - Accounts"],
        summary="어드민 회원 목록 조회",
        responses={200: AdminAccountListSerializer(many=True)},
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)

    def handle_exception(self, exc: Exception) -> Response:
        """
        명세서의 에러 응답 형식 (error_detail) 커스터마이징
        """
        response = super().handle_exception(exc)

        # 401 Unauthorized
        if response.status_code == 401:
            response.data = {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."}

        # 403 Forbidden
        elif response.status_code == 403:
            response.data = {"error_detail": "권한이 없습니다."}

        return response
