from typing import Optional

from django.db.models import QuerySet

from apps.posts.exceptions.comment_exceptions import CommentNotFoundException
from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment


class CommentSelector:
    """
    댓글 조회 및 데이터 추출을 담당하는 셀렉터 클래스입니다.
    """

    @staticmethod
    def get_comments_for_post(post_id: int) -> QuerySet[PostComment]:
        """
        특정 게시글의 댓글 목록을 조회합니다.
        author, tags__tagged_user 프리패치 포함, 생성일 기준 오름차순 정렬
        Args:
            post_id (int): 게시글 PK
        Returns:
            QuerySet[PostComment]: 해당 게시글의 댓글 목록 쿼리셋
        Raises:
            CommentNotFoundException: 게시글이 존재하지 않을 때
        """
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise CommentNotFoundException()
        return (
            PostComment.objects.filter(post=post)
            .select_related("author")
            .prefetch_related("tags__tagged_user")
            .order_by("created_at")
        )

    @staticmethod
    def get_comment_by_id(comment_id: int) -> PostComment:
        """
        pk로 단일 댓글 조회
        Args:
            comment_id (int): 댓글 PK
        Returns:
            PostComment: 해당 댓글 객체
        Raises:
            CommentNotFoundException: 댓글이 존재하지 않을 때
        """
        try:
            return PostComment.objects.get(pk=comment_id)
        except PostComment.DoesNotExist:
            raise CommentNotFoundException()
