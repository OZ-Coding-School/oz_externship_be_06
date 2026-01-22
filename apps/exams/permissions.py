from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.models import User


class IsStudentRole(BasePermission):
    message = "권한이 없습니다."

    def has_permission(self, request: Any, view: Any) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.role == User.Role.STUDENT)


class IsExamStaff(BasePermission):
    """쪽지시험 관리자 API용 권한 검사."""
    message = "쪽지시험 문제 등록 권한이 없습니다."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.role in {
            User.Role.ADMIN,
            User.Role.TA,
            User.Role.LC,
            User.Role.OM,
        }
