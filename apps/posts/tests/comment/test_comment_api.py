from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory


class PostCommentDetailAPITestCase(APITestCase):
    COMMENT_NOT_FOUND_MSG = CommentErrorMessage.COMMENT_NOT_FOUND

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass",
            nickname="testuser",
            phone_number="010-1234-5678",
            gender="MALE",
            birthday="2000-01-01",
        )
        self.category = PostCategory.objects.create(name="test category")
        self.post = Post.objects.create(
            author=self.user,
            title="test post",
            content="test content",
            category=self.category,
        )
        self.client.force_authenticate(user=self.user)

    def test_comment_detail_success(self) -> None:
        url = reverse("posts:post-comment-rud", args=[self.post.id, 1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.data)
        self.assertIn("content", response.data)
        self.assertEqual(response.data["id"], 1)

    def test_comment_detail_not_found(self) -> None:
        url = reverse("posts:post-comment-rud", args=[self.post.id, 999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], self.COMMENT_NOT_FOUND_MSG)
