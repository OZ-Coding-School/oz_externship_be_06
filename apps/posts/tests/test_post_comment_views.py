from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment

User = get_user_model()


class PostCommentAPITestCase(TestCase):
    """PostComment API 뷰 테스트"""

    def setUp(self) -> None:
        """테스트 데이터 설정"""
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.category = PostCategory.objects.create(name="테스트 카테고리", status=True)
        self.post = Post.objects.create(
            title="테스트 게시글", content="테스트 내용", author=self.user, category=self.category
        )
        self.comment = PostComment.objects.create(author=self.user, post=self.post, content="테스트 댓글")

    def test_comment_list_get(self) -> None:
        """댓글 목록 조회 테스트"""
        response = self.client.get("/api/posts/1/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data: Any = getattr(response, "data", None)
        self.assertIsInstance(data, list)

    def test_comment_create_post(self) -> None:
        """댓글 생성 테스트"""
        data = {"content": "새 댓글"}
        response = self.client.post("/api/posts/1/comments/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_retrieve_get(self) -> None:
        """댓글 상세 조회 테스트"""
        response = self.client.get(f"/api/posts/1/comments/{self.comment.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data: Any = getattr(response, "data", None)
        self.assertIn("content", data)

    def test_comment_update_put(self) -> None:
        """댓글 수정 테스트"""
        data = {"content": "수정된 댓글"}
        response = self.client.put(f"/api/posts/1/comments/{self.comment.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_delete(self) -> None:
        """댓글 삭제 테스트"""
        response = self.client.delete(f"/api/posts/1/comments/{self.comment.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
