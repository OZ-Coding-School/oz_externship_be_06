from typing import Any

from django.db import transaction

from apps.posts.exceptions.comment_exceptions import CommentForbiddenException
from apps.posts.models.post_comment import PostComment
from apps.posts.services.comment.comment_tagging_services import process_comment_tagging


@transaction.atomic
def update_comment(user: Any, comment: PostComment, content: str) -> PostComment:
    """
    기존 댓글의 내용을 수정하고, 변경된 본문에 따라 유저 태깅 정보를 갱신합니다.

    Args:
        user (Any): 수정을 시도하는 사용자 객체
        comment (PostComment): 수정 대상 댓글 객체
        content (str): 새로운 댓글 본문 내용
    Returns:
        PostComment: 수정 완료된 댓글 객체
    Raises:
        CommentForbiddenException: 요청자가 작성자가 아닐 경우 발생
    """
    # 1. 권한 검증: 댓글 작성자 본인인지 확인합니다.
    if comment.author != user:
        raise CommentForbiddenException()

    # 2. 본문 내용을 수정하고 수정 시각을 갱신합니다.
    comment.content = content
    comment.save(update_fields=["content", "updated_at"])

    # 3. 변경된 본문에 맞춰 태깅 정보를 최신화합니다.
    # (내부적으로 기존 태그 삭제 후 재성성 프로세스 진행)
    process_comment_tagging(comment, content)

    return comment
