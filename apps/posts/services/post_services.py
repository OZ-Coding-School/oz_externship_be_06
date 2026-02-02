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
        attachments: Optional[List[str]] = None
    ) -> Post:
        """요구사항에 맞춰 게시글과 관련 파일들을 원자적으로 생성합니다."""
        post: Post = Post.objects.create(
            author=user,
            category_id=category_id,
            title=title,
            content=content
        )

        if images:
            PostImage.objects.bulk_create([
                PostImage(post=post, img_url=url) for url in images
            ])

        if attachments:
            PostAttachment.objects.bulk_create([
                PostAttachment(post=post, file_url=url) for url in attachments
            ])

        return post

class PostSelector:
    """
    게시글 조회 및 데이터 추출을 담당하는 셀렉터 클래스입니다.
    """
    @staticmethod  # mypy [misc] 에러 해결을 위해 추가
    def get_post_list(
        category_id: Optional[int] = None,
        search_keyword: Optional[str] = None
    ) -> QuerySet[Post]:
        """최적화된 쿼리를 통해 게시글 목록을 반환합니다."""
        queryset: QuerySet[Post] = Post.objects.select_related('author', 'category').all().order_by('-created_at')

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if search_keyword:
            queryset = queryset.filter(
                Q(title__icontains=search_keyword) |
                Q(content__icontains=search_keyword) |
                Q(author__nickname__icontains=search_keyword)
            )

        return queryset