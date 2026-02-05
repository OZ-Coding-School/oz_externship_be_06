from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.models import Post, PostCategory, PostComment


class PostCommentDetailAPITestCase(APITestCase):
    """댓글 상세 조회 API 테스트 - 정상 조회, 댓글 미존재 시 예외"""

    COMMENT_NOT_FOUND_MSG = CommentErrorMessage.COMMENT_NOT_FOUND

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            email="detailuser@example.com",
            password="testpass",
            nickname="detailusr",
            phone_number="010-1234-5678",
            gender="MALE",
            birthday="2000-01-01",
        )
        self.category = PostCategory.objects.create(name="detail category")
        self.post = Post.objects.create(
            author=self.user,
            title="detail post",
            content="detail content",
            category=self.category,
        )
        self.comment = PostComment.objects.create(
            author=self.user,
            post=self.post,
            content="작성자 댓글",
        )

    def test_comment_detail_safe_methods_permission(self) -> None:
        """작성자/비작성자/비로그인 모두 GET 가능"""
        url = reverse("posts:post-comment-update", args=[self.post.id, self.comment.id])

        # 작성자
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 비작성자
        other_user = get_user_model().objects.create_user(
            email="otheruser@example.com",
            password="testpass",
            nickname="otheruser",
            phone_number="010-0000-0000",
            gender="FEMALE",
            birthday="1999-09-09",
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 비로그인
        self.client.force_authenticate(user=None)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_comment_detail_success(self) -> None:
        """댓글 상세 조회 성공"""
        url = reverse("posts:post-comment-update", args=[self.post.id, self.comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.data)
        self.assertIn("content", response.data)
        self.assertEqual(response.data["id"], self.comment.id)

    def test_comment_detail_not_found(self) -> None:
        """존재하지 않는 댓글 조회 시 404 반환"""
        url = reverse("posts:post-comment-update", args=[self.post.id, 999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], self.COMMENT_NOT_FOUND_MSG)
