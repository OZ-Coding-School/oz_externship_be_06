from typing import Any

from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment


def create_comment(author: Any, post: Post, content: str) -> PostComment:
    """
    댓글 생성
    """
    return PostComment.objects.create(author=author, post=post, content=content)
