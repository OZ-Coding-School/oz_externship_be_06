from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.models import User


# 조교 러닝코치 운매 관리자 검사
class IsStaffOrAdmin(BasePermission):

    message = "이 리소스에 접근할 권한이 없습니다."

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
