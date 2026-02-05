from typing import Any, List, Optional

from django.db import transaction
from django.db.models import F, Q, QuerySet

from apps.posts.exceptions.post_exceptions import (
    PostNotFoundException,
    PostPermissionDeniedException,
)
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
        """
        게시글 생성
        """

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

        post.view_count = F("view_count") + 1
        post.save(update_fields=["view_count"])

    @staticmethod
    @transaction.atomic
    def update_post(user: User, post: Post, **data: Any) -> Post:
        """
        게시글 수정
        - 요청자가 작성자인지 권한 검증 필요
        - 전달된 데이터만 선택적 업데이트
        """

        # 권한 검증 : 작성자 본인이 아니면 예외 발생
        if post.author != user:  # 작성자(post.author) 요청자(user)
            raise PostPermissionDeniedException()

        # 데이터 업데이트 및 변경된 필드 추적
        updated_fields = []
        for attr, value in data.items():
            if hasattr(post, attr):
                setattr(post, attr, value)
                updated_fields.append(attr)

        # DB 저장
        if updated_fields:
            if "updated_at" not in updated_fields:
                updated_fields.append("updated_at")

            post.save(update_fields=updated_fields)

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
