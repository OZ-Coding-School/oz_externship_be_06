from typing import Any

from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment


def create_comment(author: Any, post: Post, content: str) -> PostComment:
    # 댓글을 생성하는 함수입니다. author(작성자), post(게시글), content(내용)를 받아 댓글 객체를 생성합니다.
    return PostComment.objects.create(author=author, post=post, content=content)
