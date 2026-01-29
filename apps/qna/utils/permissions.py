from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from apps.qna.exceptions.question_e import QuestionPermissionDeniedException
from apps.qna.utils.constants import ErrorMessages


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


class CanWriteAnswer(BasePermission):
    """
    답변 작성 권한 검증
    - 허용 role: STUDENT, TA, LC, OM, ADMIN
    - 제외 role: USER (일반회원)
    """

    ALLOWED_ROLES = {"STUDENT", "TA", "LC", "OM", "ADMIN"}

    def has_permission(self, request: Request, view: Any) -> bool:
        # 로그인하지 않은 경우
        if not request.user or not request.user.is_authenticated:
            return False

        # 유저의 role이 ALLOWED_ROLES이 아닌 경우
        user_role = getattr(request.user, "role", None)
        if not user_role or str(user_role).upper() not in self.ALLOWED_ROLES:
            raise QuestionPermissionDeniedException(detail=ErrorMessages.FORBIDDEN_ANSWER_CREATE.value)

        return True
