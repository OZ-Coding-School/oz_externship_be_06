from typing import Any, Dict

from apps.posts.constants.post_const import PostErrorMessage
from apps.posts.models import Post, PostComment


def validate_comment_create(attrs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    댓글 생성 시 입력값과 요청 정보를 검증합니다.
    - 인증된 사용자만 댓글 작성 가능
    - context에 post 객체가 반드시 포함되어야 함
    - 예외 발생 시 DRF 예외 반환
    """
    request = context.get("request")
    user = getattr(request, "user", None) if request is not None else None
    if request is None or not user or not user.is_authenticated:
        from rest_framework.exceptions import NotAuthenticated

        from apps.posts.constants.post_const import PostErrorMessage

        raise NotAuthenticated(detail=PostErrorMessage.UNAUTHORIZED)

    context_post = context.get("post")
    from apps.posts.models.post import Post

    if context_post is None or not isinstance(context_post, Post):
        from rest_framework.exceptions import NotFound

        from apps.posts.constants.post_const import PostErrorMessage

        raise NotFound(detail=PostErrorMessage.POST_NOT_FOUND_WITH_TARGET)
    return attrs


def validate_comment_update(attrs: Dict[str, Any], context: Dict[str, Any], instance: PostComment) -> Dict[str, Any]:
    """
    댓글 수정 시 입력값과 요청 정보를 검증합니다.
    - 인증된 사용자만 댓글 수정 가능
    - 댓글 작성자만 본인 댓글 수정 가능
    - 예외 발생 시 DRF 예외 반환
    """
    request = context.get("request")
    user = getattr(request, "user", None) if request is not None else None
    if request is None or not user or not user.is_authenticated:
        from rest_framework.exceptions import NotAuthenticated

        from apps.posts.constants.post_const import PostErrorMessage

        raise NotAuthenticated(detail=PostErrorMessage.UNAUTHORIZED)

    if instance is not None and instance.author != user:
        from rest_framework.exceptions import PermissionDenied

        from apps.posts.constants.post_const import PostErrorMessage

        raise PermissionDenied(detail=PostErrorMessage.FORBIDDEN)
    return attrs
