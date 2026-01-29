from typing import Any
from django.db.models import Q
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.admin.account_serializers import (
    AdminAccountListSerializer,
    AdminAccountDetailSerializer
)

class AdminAccountPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class AdminUserListView(generics.ListAPIView[Any]):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = AdminAccountListSerializer
    pagination_class = AdminAccountPagination

    def get_queryset(self) -> QuerySet[User]:
        queryset = User.objects.select_related("withdrawal").all().order_by("-created_at")
        search = self.request.query_params.get("search")
        status_param = self.request.query_params.get("status")
        role_param = self.request.query_params.get("role")

        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) | Q(nickname__icontains=search) | Q(name__icontains=search)
            )

        if status_param:
            if status_param == "active":
                queryset = queryset.filter(is_active=True, withdrawal__isnull=True)
            elif status_param == "inactive":
                queryset = queryset.filter(is_active=False)
            elif status_param == "withdrew":
                queryset = queryset.filter(withdrawal__isnull=False)

        if role_param:
            role_map = {
                "admin": "ADMIN", "ta": "TA", "om": "OM",
                "lc": "LC", "user": "USER", "student": "STUDENT"
            }
            target_role = role_map.get(role_param.lower())
            if target_role:
                queryset = queryset.filter(role=target_role)
        return queryset

    @extend_schema(tags=["Admin - Accounts"], summary="어드민 회원 목록 조회")
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)

    def handle_exception(self, exc: Exception) -> Response:
        response = super().handle_exception(exc)
        if response.status_code == 401:
            response.data = {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."}
        elif response.status_code == 403:
            response.data = {"error_detail": "권한이 없습니다."}
        return response

class AdminAccountDetailView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(tags=["Admin - Accounts"], summary="어드민 회원 상세 조회")
    def get(self, request: Request, account_id: int, *args: Any, **kwargs: Any) -> Response:
        # source 명칭 변경에 맞춰 prefetch_related 경로도 enrollment_set으로 수정
        user = get_object_or_404(
            User.objects.select_related("withdrawal").prefetch_related(
                "enrollment_set__course",
                "enrollment_set__cohort"
            ),
            id=account_id
        )
        serializer = AdminAccountDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def handle_exception(self, exc: Exception) -> Response:
        response = super().handle_exception(exc)
        if response.status_code == 401:
            response.data = {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."}
        elif response.status_code == 403:
            response.data = {"error_detail": "권한이 없습니다."}
        elif response.status_code == 404:
            response.data = {"error_detail": "사용자 정보를 찾을 수 없습니다."}
        return response