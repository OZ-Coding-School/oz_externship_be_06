from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.models import User


# 어드민 페이지 접근 권한 검사
class IsAdminStaff(BasePermission):

    message = "권한이 없습니다."

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


# 어드민 전용 권한 검사
class IsAdmin(BasePermission):

    message = "권한이 없습니다."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.role == User.Role.ADMIN
