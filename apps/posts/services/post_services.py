from typing import List, Optional

from django.db import transaction
from django.db.models import Q, QuerySet

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
        """요구사항에 맞춰 게시글과 관련 파일들을 원자적으로 생성합니다."""
        post: Post = Post.objects.create(author=user, category_id=category_id, title=title, content=content)

        if images:
            PostImage.objects.bulk_create([PostImage(post=post, img_url=url) for url in images])

        if attachments:
            PostAttachment.objects.bulk_create([PostAttachment(post=post, file_url=url) for url in attachments])

        return post
