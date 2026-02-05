from __future__ import annotations

from dataclasses import dataclass
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
    """댓글 수정 시리얼라이저 테스트"""

    def test_update_serializer_validate_method(self) -> None:
        """validate 메서드가 정상적으로 호출되는지 확인"""
        factory = APIRequestFactory()
        request = factory.post("/dummy-url/")
        request.user = self.user
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "valid content"},
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_update_serializer_update_content_blank(self) -> None:
        """update에서 content가 공백일 때 ValidationError 발생"""
        factory = APIRequestFactory()
        request = factory.post("/dummy-url/")
        request.user = self.user
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "   "},
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_update_serializer_update_called(self) -> None:
        """update 메서드가 정상적으로 호출되는지 확인"""
        factory = APIRequestFactory()
        request = factory.post("/dummy-url/")
        request.user = self.user
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "update test"},
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.content, "update test")

    def setUp(self) -> None:
        """테스트용 유저, 카테고리, 게시글, 댓글 생성"""
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
        self.comment = PostComment.objects.create(post=self.post, author=self.user, content="original comment")

    def test_update_serializer_rejects_blank_content(self) -> None:
        """빈 문자열 content 거부"""
        factory = APIRequestFactory()
        request = factory.post("/dummy-url/")
        request.user = self.user
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "   "},
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_update_serializer_rejects_too_long_content(self) -> None:
        """500자 초과 content 거부"""
        factory = APIRequestFactory()
        request = factory.post("/dummy-url/")
        request.user = self.user
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "a" * 501},
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_update_serializer_success_updates_comment(self) -> None:
        """정상적으로 댓글 수정 성공"""
        factory = APIRequestFactory()
        request = factory.post("/dummy-url/")
        request.user = self.user
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "updated content"},
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        updated = serializer.save()

        self.assertEqual(updated.content, "updated content")
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "updated content")

    def test_update_serializer_not_author_raises(self) -> None:
        """작성자가 아닌 사용자가 수정 시도 시 예외 발생"""
        factory = APIRequestFactory()
        request = factory.post("/dummy-url/")
        request.user = self.other_user
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "hijack"},
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # 서비스에서 CommentForbiddenException이 올라오는 구조
        with self.assertRaises(CommentForbiddenException):
            serializer.save()

    def test_update_serializer_unauthenticated_user_raises(self) -> None:
        """비인증 유저는 예외 발생"""
        factory = APIRequestFactory()
        request = factory.post("/dummy-url/")
        # 비인증 유저 시나리오
        request.user = AnonymousUser()
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "updated"},
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # user=None이면 보통 권한/인증 예외가 발생
        with self.assertRaises(Exception):
            serializer.save()



class PostCommentUpdateServiceTests(TestCase):
    """댓글 수정 서비스 테스트"""

    def test_update_comment_with_none_user_raises(self) -> None:
        """user가 None이면 예외 발생"""
        with self.assertRaises(Exception):
            update_comment(None, self.comment, "수정")

    def setUp(self) -> None:
        """테스트용 유저, 카테고리, 게시글, 댓글 생성"""
        User = get_user_model()
        self.user = User.objects.create_user(email="test@example.com", password="testpass", nickname="user")
        self.other_user = User.objects.create_user(email="other@example.com", password="testpass", nickname="other")
        self.category = PostCategory.objects.create(name="cat")
        self.post = Post.objects.create(author=self.user, title="t", content="c", category=self.category)
        self.comment = PostComment.objects.create(post=self.post, author=self.user, content="cc")

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
        """테스트용 유저, 카테고리, 게시글, 댓글, URL 생성"""
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
        """잘못된 comment id로 요청 시 404 반환"""
        self.client.force_authenticate(user=self.user)
        for invalid_id in [None, 0, -1]:
            url = reverse("posts:post-comment-update", args=[invalid_id if invalid_id is not None else 0])
            response = self.client.put(url, {"content": "updated comment"}, format="json")
            self.assertEqual(response.status_code, 404)
            self.assertIn("error_detail", response.data)
