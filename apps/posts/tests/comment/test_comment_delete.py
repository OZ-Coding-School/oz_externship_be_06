from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.exceptions.comment_exceptions import CommentForbiddenException
from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment
from apps.posts.services.comment.comment_delete_services import delete_comment


class PostCommentDeleteServiceTests(TestCase):
    """댓글 삭제 서비스 테스트"""

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass",
            nickname="user",
            phone_number="010-0000-0000",
            gender="MALE",
            birthday="1990-01-01",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass",
            nickname="other",
            phone_number="010-1111-2222",
            gender="FEMALE",
            birthday="1991-02-02",
        )
        self.category = PostCategory.objects.create(name="cat")
        self.post = Post.objects.create(author=self.user, title="t", content="c", category=self.category)
        self.comment = PostComment.objects.create(post=self.post, author=self.user, content="cc")

    def test_delete_comment_with_invalid_user(self) -> None:
        """user가 None이거나 잘못된 경우 예외 발생"""
        with self.assertRaises(Exception):
            delete_comment(None, self.comment)

    def test_delete_comment_with_none_comment(self) -> None:
        """comment가 None이면 예외 발생"""
        with self.assertRaises(Exception):
            delete_comment(self.user, None)  # type: ignore[arg-type]

    def test_delete_comment_not_author(self) -> None:
        """작성자가 아닌 사용자가 삭제 시도 시 예외 발생"""
        with self.assertRaises(CommentForbiddenException):
            delete_comment(self.other_user, self.comment)

    def test_delete_comment_success(self) -> None:
        """정상적으로 댓글 삭제 성공"""
        comment = PostComment.objects.create(post=self.post, author=self.user, content="삭제 테스트")
        delete_comment(self.user, comment)
        self.assertFalse(PostComment.objects.filter(id=comment.id).exists())


class PostCommentDeleteAPITests(TestCase):
    """댓글 삭제 API 테스트 - 인증, 권한, 예외, 정상 삭제"""

    def setUp(self) -> None:
        self.client = APIClient()
        User = get_user_model()

        self.author = User.objects.create_user(
            email="author@example.com",
            password="testpass",
            nickname="author",
            phone_number="010-1111-2222",
            gender="MALE",
            birthday="1990-01-01",
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            password="testpass",
            nickname="other",
            phone_number="010-3333-4444",
            gender="FEMALE",
            birthday="1995-05-05",
        )

        self.category = PostCategory.objects.create(name="cat")
        self.post = Post.objects.create(
            author=self.author,
            title="t",
            content="c",
            category=self.category,
        )
        self.comment = PostComment.objects.create(
            post=self.post,
            author=self.author,
            content="hi",
        )

    def _url(self, comment_id: int) -> str:
        """urls.py: "<int:post_id>/comments/<int:comment_id>/delete/" """
        return reverse("posts:post-comment-delete", args=[self.post.id, comment_id])

    def test_delete_401_when_unauthenticated(self) -> None:
        res = self.client.delete(self._url(self.comment.id))
        self.assertEqual(res.status_code, 401)
        self.assertIn("error_detail", res.data)  # type: ignore[attr-defined]
        self.assertEqual(res.data["error_detail"], CommentErrorMessage.UNAUTHORIZED)  # type: ignore[attr-defined]

    def test_delete_403_when_not_author(self) -> None:
        self.client.force_authenticate(user=self.other)  # type: ignore[attr-defined]
        res = self.client.delete(self._url(self.comment.id))
        self.assertEqual(res.status_code, 403)
        self.assertIn("error_detail", res.data)  # type: ignore[attr-defined]
        self.assertEqual(res.data["error_detail"], CommentErrorMessage.FORBIDDEN)  # type: ignore[attr-defined]

        """삭제 안 됐는지 확인"""
        self.assertTrue(PostComment.objects.filter(id=self.comment.id).exists())

    def test_delete_404_when_comment_id_non_positive(self) -> None:
        self.client.force_authenticate(user=self.author)  # type: ignore[attr-defined]
        res = self.client.delete(self._url(0))
        self.assertEqual(res.status_code, 404)
        self.assertIn("error_detail", res.data)  # type: ignore[attr-defined]
        self.assertEqual(res.data["error_detail"], CommentErrorMessage.COMMENT_NOT_FOUND)  # type: ignore[attr-defined]

    def test_delete_404_when_comment_id_magic_999999(self) -> None:
        self.client.force_authenticate(user=self.author)  # type: ignore[attr-defined]
        res = self.client.delete(self._url(999999))
        self.assertEqual(res.status_code, 404)
        self.assertIn("error_detail", res.data)  # type: ignore[attr-defined]
        self.assertEqual(res.data["error_detail"], CommentErrorMessage.COMMENT_NOT_FOUND)  # type: ignore[attr-defined]

    def test_delete_200_success_and_db_deleted(self) -> None:
        self.client.force_authenticate(user=self.author)  # type: ignore[attr-defined]
        res = self.client.delete(self._url(self.comment.id))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["detail"], "댓글이 삭제되었습니다.")  # type: ignore[attr-defined]
        self.assertFalse(PostComment.objects.filter(id=self.comment.id).exists())
