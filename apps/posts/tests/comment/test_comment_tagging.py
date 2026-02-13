from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment
from apps.posts.models.post_comment_tags import PostCommentTag
from apps.users.models import User


class CommentTaggingTests(TestCase):
    """댓글 유저 태깅 기능 테스트"""

    user: User
    other_user: User
    category: PostCategory
    post: Post
    list_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="tag_test@example.com",
            password="password",
            name="테스트",
            nickname="testuser",
            phone_number="01011112222",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
            is_active=True,
        )
        cls.other_user = User.objects.create_user(
            email="tag_other@example.com",
            password="password",
            name="태그대상",
            nickname="taggeduser",
            phone_number="01033334444",
            gender=User.Gender.FEMALE,
            birthday=date(1992, 2, 2),
            is_active=True,
        )
        cls.category = PostCategory.objects.create(name="태그테스트카테고리")
        cls.post = Post.objects.create(
            author=cls.user,
            title="태그 테스트 게시글",
            content="태그 테스트용 게시글",
            category=cls.category,
        )
        cls.list_url = f"/api/v1/posts/{cls.post.id}/comments"

    def setUp(self) -> None:
        self.client = APIClient()
        token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_comment_with_tag(self) -> None:
        """댓글 작성 시 유저 태그가 정상적으로 저장되는지 테스트"""
        content = "@taggeduser 안녕하세요!"
        response = self.client.post(self.list_url, {"content": content}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        comment = PostComment.objects.get(post=self.post, content=content)
        tags = PostCommentTag.objects.filter(comment=comment)
        self.assertEqual(tags.count(), 1)
        tag = tags.first()
        self.assertIsNotNone(tag)
        if tag:
            self.assertEqual(tag.tagged_user, self.other_user)

    def test_update_comment_tag(self) -> None:
        """댓글 수정 시 유저 태그가 갱신되는지 테스트"""
        comment = PostComment.objects.create(post=self.post, author=self.user, content="기존 내용")
        detail_url = f"/api/v1/posts/{self.post.id}/comments/{comment.id}"

        new_content = "@taggeduser 수정된 내용"
        response = self.client.put(detail_url, {"content": new_content}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.content, new_content)

        tags = PostCommentTag.objects.filter(comment=comment)
        self.assertEqual(tags.count(), 1)
        tag = tags.first()
        self.assertIsNotNone(tag)
        if tag:
            self.assertEqual(tag.tagged_user, self.other_user)

    def test_invalid_user_tag_ignored(self) -> None:
        """존재하지 않는 유저 태그 시 무시되는지 테스트"""
        content = "@noneuser 존재하지 않는 유저"
        response = self.client.post(self.list_url, {"content": content}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = PostComment.objects.get(post=self.post, content=content)
        self.assertFalse(PostCommentTag.objects.filter(comment=comment).exists())
