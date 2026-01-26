from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from apps.qna.exceptions.question_exception import (
    QuestionPermissionDeniedException,
)


class IsStudent(BasePermission):
    """
    수강생 권한 검증
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """role이 STUDENT인지 검증"""
        user_role = getattr(request.user, "role", None)
        if not user_role or str(user_role) != "STUDENT":
            raise QuestionPermissionDeniedException()

        return True  # user_role이 STUDENT일때 True
