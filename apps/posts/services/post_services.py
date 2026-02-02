from typing import List, Optional

from django.db import transaction
from django.db.models import Q, QuerySet, F

from apps.posts.models import Post, PostAttachment, PostImage
from apps.users.models import User


class PostService:
    """
    게시글 관련 생성/수정/삭제 비즈니스 로직을 담당하는 서비스 클래스입니다.
    """

    @staticmethod
    @transaction.atomic
    def create_post(
        user: User,
        category_id: int,
        title: str,
        content: str,
        images: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
    ) -> Post:

        post: Post = Post.objects.create(author=user, category_id=category_id, title=title, content=content)

        if images:
            PostImage.objects.bulk_create([PostImage(post=post, img_url=url) for url in images])

        if attachments:
            PostAttachment.objects.bulk_create([PostAttachment(post=post, file_url=url) for url in attachments])

        return post

    @staticmethod
    def increment_view_count(post: Post) -> None:
        """
        게시글의 조회수를 1 증가
        F 객체를 사용 Race Condition 방지
        동시에 처리되면 안 되는 작업이 동시에 처리돼서 값이 깨지는 것
        F 객체 : 경쟁 상태 없음, 순서 상관없음, 안전
        """

        post.view_count = F('view_count') + 1
        post.save(update_fields=['view_count'])