from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from apps.qna.exceptions.question_exception import (
    QuestionAuthenticationRequiredException,
    QuestionPermissionDeniedException,
)


class IsStudent(BasePermission):
    """
    수강생 권한 검증
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        if not (request.user and request.user.is_authenticated):  # 로그인 여부 확인
            raise QuestionAuthenticationRequiredException()

        user_role = getattr(request.user, "role", None)
        if not user_role or str(user_role) != "STUDENT":
            raise QuestionPermissionDeniedException()

        return True  # user_role이 STUDENT일때 True
