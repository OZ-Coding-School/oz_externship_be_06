from typing import Any

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.posts.constants.post_const import PostErrorMessage
from apps.posts.models import Post, PostCategory
from apps.users.models import User


class PostDeleteTest(APITestCase):
    """
    게시글 삭제 API의 권한 및 비즈니스 로직을 검증하는 테스트 클래스입니다.
    """

    author: User
    other_user: User
    admin_user: User
    post: Post
    category: PostCategory

    @classmethod
    def setUpTestData(cls) -> None:
        """
        테스트 실행 전 필수 필드를 포함하여 유저를 생성합니다.
        """
        # 1. 테스트용 유저 생성 (필수 필드 포함: name, nickname, email, birthday, gender, phone_number)
        cls.author = User.objects.create_user(
            email="author@test.com",
            password="password123",
            nickname="작성자",
            name="김작성",
            birthday="1990-01-01",
            gender="MALE",
            phone_number="010-1111-1111",
            role="general",
        )
        cls.other_user = User.objects.create_user(
            email="other@test.com",
            password="password123",
            nickname="일반유저",
            name="이일반",
            birthday="1992-02-02",
            gender="FEMALE",
            phone_number="010-2222-2222",
            role="general",
        )
        cls.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="password123",
            nickname="관리자",
            name="박관리",
            birthday="1985-05-05",
            gender="MALE",
            phone_number="010-3333-3333",
            role="admin",
        )

        cls.category = PostCategory.objects.create(name="테스트 카테고리", status=True)

    def setUp(self) -> None:
        self.post = Post.objects.create(
            author=self.author, title="삭제 테스트 제목", content="삭제 테스트 내용", category=self.category
        )
        self.url = reverse("posts:post-detail", kwargs={"post_id": self.post.id})

    # ... 이하 테스트 메서드(test_delete_post_success_by_author 등)는 동일 ...
