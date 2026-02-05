from typing import Any

from django.db import transaction

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.exceptions.comment_exceptions import (
    CommentForbiddenException,
    CommentNotFoundException,
)
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
    def get_comment_for_update(user: Any, comment_id: int) -> PostComment:
        """
        댓글 수정/삭제 전용: 댓글 조회 및 권한 체크
        """
        try:
            comment = PostComment.objects.get(pk=comment_id)
        except PostComment.DoesNotExist:
            raise CommentNotFoundException()
        if comment.author != user:
            raise CommentForbiddenException()
        return comment

    @staticmethod
    @transaction.atomic
    def update_comment(user: Any, comment: PostComment, content: str) -> PostComment:
        """
        댓글 수정 (작성자만 가능)
        """
        # 권한 체크는 get_comment_for_update에서 이미 수행됨
        comment.content = content
        comment.save(update_fields=["content", "updated_at"])
        return comment

    @staticmethod
    @transaction.atomic
    def delete_comment(user: Any, comment: PostComment) -> None:
        """
        댓글 삭제 (작성자만 가능)
        """
        # 권한 체크는 get_comment_for_update에서 이미 수행됨
        comment.delete()
