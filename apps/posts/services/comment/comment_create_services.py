from typing import Any

from django.db import transaction

from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment
from apps.posts.services.comment.comment_tagging_services import process_comment_tagging


@transaction.atomic
def create_comment(author: Any, post: Post, content: str) -> PostComment:
    """
    새로운 댓글을 생성하고, 본문 내 유저 태깅을 처리합니다.

    Args:
        author (Any): 댓글 작성자 (User 객체)
        post (Post): 댓글이 달릴 게시글 객체
        content (str): 댓글 본문 내용
    Returns:
        PostComment: 생성된 댓글 객체
    """
    # 1. 댓글 기본 정보를 DB에 저장합니다.
    comment = PostComment.objects.create(author=author, post=post, content=content)

    # 2. 본문 텍스트를 분석하여 태깅된 유저 정보를 저장합니다.
    process_comment_tagging(comment, content)

    return comment
