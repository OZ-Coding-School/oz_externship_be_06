from typing import Any

from django.db import transaction
from rest_framework.exceptions import PermissionDenied

from apps.posts.constants.post_const import PostErrorMessage
from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment


class PostCommentService:
    """
    댓글 관련 비즈니스 로직을 담당하는 서비스 클래스입니다.
    """

    @staticmethod
    @transaction.atomic
    def create_comment(author: Any, post: Post, content: str) -> PostComment:
        """
        댓글 생성
        """
        return PostComment.objects.create(author=author, post=post, content=content)

    @staticmethod
    @transaction.atomic
    def update_comment(user: Any, comment: PostComment, content: str) -> PostComment:
        """
        댓글 수정 (작성자만 가능)
        """
        if comment.author != user:
            raise PermissionDenied(PostErrorMessage.FORBIDDEN)
        comment.content = content
        comment.save(update_fields=["content", "updated_at"])
        return comment

    @staticmethod
    @transaction.atomic
    def delete_comment(user: Any, comment: PostComment) -> None:
        """
        댓글 삭제 (작성자만 가능)
        """
        if comment.author != user:
            raise PermissionDenied(PostErrorMessage.FORBIDDEN)
        comment.delete()
