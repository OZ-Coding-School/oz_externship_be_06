from typing import Any

from django.views import View
from rest_framework import permissions
from rest_framework.request import Request


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(obj.author == request.user)
