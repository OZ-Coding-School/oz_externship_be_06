from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsCommentAuthorOrReadOnly(BasePermission):
    # 댓글 작성자만 수정/삭제 가능, 그 외에는 읽기만 허용하는 권한 클래스입니다.

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        # 읽기(GET, HEAD, OPTIONS)는 모두 허용
        if request.method in SAFE_METHODS:
            return True
        # 수정/삭제는 댓글 작성자만 허용
        return bool(getattr(obj, "author", None) == getattr(request, "user", None))
