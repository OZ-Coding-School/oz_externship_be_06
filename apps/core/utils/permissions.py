from __future__ import annotations

from typing import Any, Iterable, Set, Type

from rest_framework.permissions import BasePermission

from apps.users.models import User


class RolePermission(BasePermission):
    """사용자 역할 기반 권한."""

    allowed_roles: Set[User.Role] = set()
    message = "권한이 없습니다."

    def has_permission(self, request: Any, view: Any) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.role in self.allowed_roles

    @classmethod
    def with_roles(cls, roles: Iterable[User.Role]) -> Type["RolePermission"]:
        roles_set = set(roles)
        return type(
            "RolePermissionWithRoles",
            (cls,),
            {"allowed_roles": roles_set},
        )


class IsStudentRole(RolePermission):
    allowed_roles = {User.Role.STUDENT}


class IsStaffRole(RolePermission):
    """관리자/스태프 권한 검사."""

    allowed_roles = {
        User.Role.ADMIN,
        User.Role.TA,
        User.Role.LC,
        User.Role.OM,
    }
