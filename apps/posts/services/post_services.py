from typing import Any, List, Optional

from django.db import transaction
from django.db.models import F, Q, QuerySet

from apps.posts.exceptions.post_exceptions import (
    PostNotFoundException,
    PostPermissionDeniedException,
)
from apps.posts.models import Post, PostAttachment, PostImage
from apps.qna.utils.content_parser import ContentParser
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
        """
        게시글 생성
        """

        post: Post = Post.objects.create(author=user, category_id=category_id, title=title, content=content)

        # if images:
        #     PostImage.objects.bulk_create([PostImage(post=post, img_url=url) for url in images])

        if content:
            # content에서 새 이미지 URL 리스트 추출 (중복 제거를 위해 Set 사용)
            image_urls = set(ContentParser.extract_all_image_urls(post.content))

            # 이미지 생성
            if image_urls:
                PostImage.objects.bulk_create([PostImage(post=post, img_url=url) for url in image_urls])

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

        post.view_count = F("view_count") + 1
        post.save(update_fields=["view_count"])

    @staticmethod
    @transaction.atomic
    def update_post(user: User, post: Post, **data: Any) -> Post:
        """
        게시글 수정 및 이미지 썸네일 동기화
        """
        if post.author != user:
            raise PostPermissionDeniedException()

        # 1. 일반 필드 업데이트
        updated_fields = []
        content_changed = False
        for attr, value in data.items():
            if hasattr(post, attr):
                setattr(post, attr, value)
                updated_fields.append(attr)
                if attr == "content":
                    content_changed = True

        if updated_fields:
            post.save(update_fields=updated_fields)

        # 2. 본문 변경 시 이미지 테이블 동기화
        if content_changed:
            # 본문에서 현재 이미지 URL들을 순서대로 추출
            current_image_urls = ContentParser.extract_all_image_urls(post.content) # 리스트 형태 (순서 유지)

            # 실무형 로직: 기존 이미지를 모두 지우고 새로 생성하여 '첫 번째 이미지'의 순서를 보장함
            # (만약 성능 최적화가 더 중요하다면 이전 답변의 Set 연산 방식을 유지하되 ID 순서를 관리해야 함)
            post.images.all().delete()

            if current_image_urls:
                PostImage.objects.bulk_create([
                    PostImage(post=post, img_url=url) for url in current_image_urls
                ])

        return post

    @staticmethod
    @transaction.atomic
    def delete_post(post_id: int, user: User) -> None:
        """
        게시글을 삭제
        작성자 본인 혹은 관리자에게 권한 있음
        """

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise PostNotFoundException()

        # 권한 검증
        if post.author_id != user.id:
            raise PostPermissionDeniedException()

        # 게시글 삭제
        # 연관 데이터 자동 삭제 또는 수정 처리
        post.delete()
