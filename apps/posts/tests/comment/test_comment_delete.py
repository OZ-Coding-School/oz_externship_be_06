from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.exceptions.comment_exceptions import CommentForbiddenException
from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment
from apps.posts.services.comment.comment_delete_services import delete_comment



class PostCommentDeleteServiceTests(TestCase):
    """댓글 삭제 서비스 테스트"""

    def test_delete_comment_with_invalid_user(self) -> None:
        """user가 None이거나 잘못된 경우 예외 발생"""
        with self.assertRaises(Exception):
            delete_comment(None, self.comment)  # type: ignore[arg-type]

    def test_delete_comment_with_none_comment(self) -> None:
        """comment가 None이면 예외 발생"""
        with self.assertRaises(Exception):
            delete_comment(self.user, None)  # type: ignore[arg-type]

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(email="test@example.com", password="testpass", nickname="user")
        self.other_user = User.objects.create_user(email="other@example.com", password="testpass", nickname="other")
        self.category = PostCategory.objects.create(name="cat")
        self.post = Post.objects.create(author=self.user, title="t", content="c", category=self.category)
        self.comment = PostComment.objects.create(post=self.post, author=self.user, content="cc")

    def test_delete_comment_not_author(self) -> None:
        """작성자가 아닌 사용자가 삭제 시도 시 예외 발생"""
        with self.assertRaises(CommentForbiddenException):
            delete_comment(self.other_user, self.comment)

    def test_delete_comment_with_none_comment(self) -> None:
        """None을 삭제 시도 시 예외 발생"""
        with self.assertRaises(Exception):
            delete_comment(self.user, None)  # type: ignore[arg-type]

    def test_delete_comment_success(self) -> None:
        """정상적으로 댓글 삭제 성공"""
        comment = PostComment.objects.create(post=self.post, author=self.user, content="삭제 테스트")
        delete_comment(self.user, comment)
        with self.assertRaises(PostComment.DoesNotExist):
            PostComment.objects.get(id=comment.id)


class PostCommentDeleteAPITestCase(APITestCase):
    """댓글 삭제 API 테스트 - 성공, 인증 실패, 권한 실패, 미존재 댓글"""

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            email="deleteuser@example.com",
            password="testpass",
            nickname="deleteuser",
            phone_number="010-7777-8888",
            gender="MALE",
            birthday="1988-08-08",
        )
        self.other_user = User.objects.create_user(
            email="otheruser3@example.com",
            password="testpass",
            nickname="otheruser3",
            phone_number="010-9999-0000",
            gender="FEMALE",
            birthday="1993-03-03",
        )
        self.category = PostCategory.objects.create(name="delete category")
        self.post = Post.objects.create(
            author=self.user,
            title="delete post",
            content="delete content",
            category=self.category,
        )
        self.comment = PostComment.objects.create(
            author=self.user,
            post=self.post,
            content="delete comment",
        )
        self.delete_url = reverse("posts:post-comment-delete", args=[self.comment.id])

    def test_comment_delete_success(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("detail", response.data)

    def test_comment_delete_unauthenticated(self) -> None:
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.UNAUTHORIZED)

    def test_comment_delete_forbidden(self) -> None:
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 403)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.FORBIDDEN)

    def test_comment_delete_not_found(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("posts:post-comment-delete", args=[999999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.COMMENT_NOT_FOUND)

    def test_delete_comment_with_invalid_comment_id(self) -> None:
        self.client.force_authenticate(user=self.user)
        for invalid_id in [None, 0, -1]:
            url = reverse("posts:post-comment-delete", args=[invalid_id if invalid_id is not None else 0])
            response = self.client.delete(url)
            self.assertEqual(response.status_code, 404)
            self.assertIn("error_detail", response.data)
