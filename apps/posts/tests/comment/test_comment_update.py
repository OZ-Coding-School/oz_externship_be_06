from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.exceptions.comment_exceptions import CommentForbiddenException
from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment
from apps.posts.serializers.comment_serializers import PostCommentUpdateSerializer
from apps.posts.services.comment.comment_update_services import update_comment


class PostCommentUpdateSerializerTests(TestCase):
    """댓글 수정 시리얼라이저 테스트 (DB 기반)"""

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            email="updateuser@example.com",
            password="testpass",
            nickname="updateuser",
            phone_number="010-1111-2222",
            gender="MALE",
            birthday="1990-01-01",
        )
        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="testpass",
            nickname="otheruser",
            phone_number="010-3333-4444",
            gender="FEMALE",
            birthday="1995-05-05",
        )

        self.category = PostCategory.objects.create(name="update category")
        self.post = Post.objects.create(
            author=self.user,
            title="update post",
            content="update content",
            category=self.category,
        )
        self.comment = PostComment.objects.create(
            post=self.post,
            author=self.user,
            content="original comment",
        )

        self.factory = APIRequestFactory()

    def _make_request(self, user: Any) -> Any:
        request = self.factory.patch("/dummy-url/")
        request.user = user
        return request

    def test_update_serializer_rejects_blank_content(self) -> None:
        """공백 content 거부"""
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "   "},
            context={"request": self._make_request(self.user)},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_update_serializer_rejects_too_long_content(self) -> None:
        """500자 초과 content 거부"""
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "a" * 501},
            context={"request": self._make_request(self.user)},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_update_serializer_success_updates_db(self) -> None:
        """정상 수정 시 DB 반영 + 반환값 확인"""
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "updated content"},
            context={"request": self._make_request(self.user)},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        updated = serializer.save()

        self.assertEqual(updated.id, self.comment.id)
        self.assertEqual(updated.content, "updated content")

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "updated content")

    def test_update_serializer_not_author_raises(self) -> None:
        """작성자가 아닌 사용자가 수정 시도 → 예외 발생"""
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "hijack"},
            context={"request": self._make_request(self.other_user)},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        with self.assertRaises(CommentForbiddenException):
            serializer.save()

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "original comment")

    def test_update_serializer_unauthenticated_user_raises(self) -> None:
        """비인증 유저 수정 시도 → 예외 발생"""
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "updated"},
            context={"request": self._make_request(AnonymousUser())},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        with self.assertRaises(Exception):
            serializer.save()

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "original comment")


class PostCommentUpdateServiceTests(TestCase):
    """댓글 수정 서비스 테스트"""

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(email="test@example.com", password="testpass", nickname="user")
        self.other_user = User.objects.create_user(email="other@example.com", password="testpass", nickname="other")
        self.category = PostCategory.objects.create(name="cat")
        self.post = Post.objects.create(author=self.user, title="t", content="c", category=self.category)
        self.comment = PostComment.objects.create(post=self.post, author=self.user, content="cc")

    def test_update_comment_with_none_user_raises(self) -> None:
        """user가 None이면 예외 발생"""
        with self.assertRaises(Exception):
            update_comment(None, self.comment, "수정")

    def test_update_comment_not_author_raises(self) -> None:
        """작성자가 아닌 사용자가 수정 시도 시 예외 발생"""
        with self.assertRaises(CommentForbiddenException):
            update_comment(self.other_user, self.comment, "수정")

    def test_update_comment_with_none_comment_raises(self) -> None:
        """comment가 None이면 예외 발생"""
        with self.assertRaises(Exception):
            update_comment(self.user, None, "수정")  # type: ignore[arg-type]

    def test_update_comment_success(self) -> None:
        """정상적으로 댓글 수정 성공"""
        updated = update_comment(self.user, self.comment, "수정 후")
        self.assertEqual(updated.content, "수정 후")

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "수정 후")


class PostCommentUpdateAPITestCase(APITestCase):
    """댓글 수정 API 테스트 - 성공, 인증 실패, 미존재, 권한 실패, validation 실패"""

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            email="updateuser@example.com",
            password="testpass",
            nickname="updateuser",
            phone_number="010-1111-2222",
            gender="MALE",
            birthday="1990-01-01",
        )
        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="testpass",
            nickname="otheruser",
            phone_number="010-3333-4444",
            gender="FEMALE",
            birthday="1995-05-05",
        )
        self.category = PostCategory.objects.create(name="update category")
        self.post = Post.objects.create(
            author=self.user,
            title="update post",
            content="update content",
            category=self.category,
        )
        self.comment = PostComment.objects.create(
            author=self.user,
            post=self.post,
            content="original comment",
        )
        self.url = reverse("posts:post-comment-update", args=[self.comment.id])

    def test_update_comment_success(self) -> None:
        """정상적으로 댓글 수정 API 성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, {"content": "updated comment"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["content"], "updated comment")
        self.assertEqual(response.data["id"], self.comment.id)

        """DB 반영 확인"""
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "updated comment")

    def test_update_comment_success_multipart(self) -> None:
        """multipart로도 정상 수정되는지 (parser 분기 커버용)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, {"content": "multipart updated"}, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "multipart updated")

    def test_update_comment_unauthenticated(self) -> None:
        """비인증 유저는 401 반환"""
        response = self.client.put(self.url, {"content": "updated comment"}, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.UNAUTHORIZED)

    def test_update_comment_not_found(self) -> None:
        """존재하지 않는 댓글 수정 시 404 반환"""
        self.client.force_authenticate(user=self.user)
        url = reverse("posts:post-comment-update", args=[999999])
        response = self.client.put(url, {"content": "updated comment"}, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.COMMENT_NOT_FOUND)

    def test_update_comment_forbidden(self) -> None:
        """작성자가 아닌 사용자가 수정 시도 시 403 반환"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.put(self.url, {"content": "updated comment"}, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.FORBIDDEN)

    def test_update_comment_validation_error(self) -> None:
        """content validation 실패 시 400 반환"""
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, {"content": "   "}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error_detail", response.data)
        self.assertIn("content", response.data["error_detail"])

    def test_update_comment_with_invalid_comment_id(self) -> None:
        """잘못된 comment id로 요청 시 404 반환 (0, -1)"""
        self.client.force_authenticate(user=self.user)

        for invalid_id in [0, -1]:
            url = reverse("posts:post-comment-update", args=[invalid_id])
            response = self.client.put(url, {"content": "updated comment"}, format="json")
            self.assertEqual(response.status_code, 404)
            self.assertIn("error_detail", response.data)
