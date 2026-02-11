from django.db import transaction

from apps.posts.constants.post_const import PostErrorMessage
from apps.posts.exceptions.post_exceptions import PostNotFoundException
from apps.posts.models.post import Post
from apps.posts.models.post_likes import PostLike
from apps.users.models.user import User


class PostLikeService:
    """
    게시글 좋아요 관련 비즈니스 로직을 처리하는 서비스 클래스
    """

    @staticmethod
    @transaction.atomic
    def register_like(user: User, post_id: int) -> PostLike:
        """
        좋아요 등록: 멱등성을 보장하며 is_liked를 True로 설정합니다.
        """
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise PostNotFoundException()

        like, _ = PostLike.objects.update_or_create(user=user, post=post, defaults={"is_liked": True})
        return like

    @staticmethod
    @transaction.atomic
    def cancel_like(user: User, post_id: int) -> None:
        """
        좋아요 취소: 해당 유저의 좋아요 상태를 False로 업데이트합니다.
        """
        updated = PostLike.objects.filter(user=user, post_id=post_id, is_liked=True).update(is_liked=False)
        if not updated:
            raise PostNotFoundException(PostErrorMessage.LIKE_NOT_FOUND)
