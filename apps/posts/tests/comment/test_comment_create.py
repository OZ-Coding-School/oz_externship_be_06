from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Type

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.serializers.comment_serializers import PostCommentCreateSerializer
from apps.posts.services.comment.comment_create_services import create_comment


class PostCommentCreateSerializerTests(TestCase):
    """댓글 생성 시리얼라이저 테스트"""

    def setUp(self) -> None:
        """테스트용 유저, 카테고리, 게시글 생성"""
        User = get_user_model()
        self.user = User.objects.create_user(
            email="createuser@example.com",
            password="testpass",
            nickname="createuser",
            phone_number="010-5555-6666",
            gender="MALE",
            birthday="1985-02-02",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass",
            nickname="other",
            phone_number="010-1111-2222",
            gender="MALE",
            birthday="1990-01-01",
        )
        self.category = PostCategory.objects.create(name="create category")
        self.post = Post.objects.create(
            author=self.user,
            title="create post",
            content="create content",
            category=self.category,
        )

    def _make_serializer(
        self,
        *,
        content: str,
        request_user: Any = None,
        post: Any = None,
        include_request: bool = True,
    ) -> PostCommentCreateSerializer:
        """테스트용 시리얼라이저 생성 헬퍼"""
        context: dict[str, Any] = {}
        if include_request:
            factory = APIRequestFactory()
            request = factory.post("/dummy-url/")
            if request_user is not None:
                request.user = request_user
            else:
                # 비인증 유저 시나리오
                request.user = AnonymousUser()
            context["request"] = request
        if post is not None:
            context["post"] = post

        return PostCommentCreateSerializer(
            data={"content": content},
            context=context,
        )

    def test_create_serializer_rejects_blank_content(self) -> None:
        """빈 문자열 content 거부"""
        serializer = self._make_serializer(content="   ", request_user=self.user, post=self.post)
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_create_serializer_rejects_too_long_content(self) -> None:
        """500자 초과 content 거부"""
        serializer = self._make_serializer(content="a" * 501, request_user=self.user, post=self.post)
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_create_serializer_success_creates_comment(self) -> None:
        """정상적으로 댓글 생성 성공"""
        serializer = self._make_serializer(content="new comment", request_user=self.user, post=self.post)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        comment = serializer.save()
        self.assertEqual(comment.content, "new comment")
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)

    def test_create_serializer_unauthenticated_user_raises(self) -> None:
        """비인증 유저는 예외 발생"""
        serializer = self._make_serializer(content="new comment", request_user=None, post=self.post)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        from apps.posts.exceptions.comment_exceptions import (
            CommentUnauthorizedException,
        )

        with self.assertRaises(CommentUnauthorizedException):
            serializer.save()

    def test_create_serializer_no_request_in_context_raises(self) -> None:
        """request가 context에 없으면 예외 발생"""
        serializer = self._make_serializer(
            content="new comment",
            request_user=self.user,
            post=self.post,
            include_request=False,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        from apps.posts.exceptions.comment_exceptions import (
            CommentUnauthorizedException,
        )

        with self.assertRaises(CommentUnauthorizedException):
            serializer.save()

    def test_create_serializer_no_post_in_context_raises(self) -> None:
        """post가 context에 없으면 예외 발생"""
        serializer = self._make_serializer(content="new comment", request_user=self.user, post=None)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        from apps.posts.exceptions.comment_exceptions import CommentNotFoundException

        with self.assertRaises(CommentNotFoundException):
            serializer.save()

    def test_create_serializer_wrong_post_type_in_context_raises(self) -> None:
        """post 타입이 잘못된 경우 예외 발생"""
        serializer = self._make_serializer(content="new comment", request_user=self.user, post="not_a_post")
        self.assertTrue(serializer.is_valid(), serializer.errors)
        from apps.posts.exceptions.comment_exceptions import CommentNotFoundException

        with self.assertRaises(CommentNotFoundException):
            serializer.save()


class PostCommentCreateServiceTests(TestCase):
    """댓글 생성 서비스 테스트"""

    def setUp(self) -> None:
        """테스트용 유저, 카테고리, 게시글 생성"""
        User = get_user_model()
        self.user = User.objects.create_user(email="test@example.com", password="testpass", nickname="user")
        self.category = PostCategory.objects.create(name="cat")
        self.post = Post.objects.create(author=self.user, title="t", content="c", category=self.category)

    def test_create_comment_success(self) -> None:
        """정상적으로 댓글 생성 성공"""
        comment = create_comment(author=self.user, post=self.post, content="서비스 댓글")
        self.assertEqual(comment.content, "서비스 댓글")
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)

    def test_create_comment_with_none_post_raises(self) -> None:
        """post가 None이면 예외 발생"""
        with self.assertRaises(Exception):
            pass

    def test_create_comment_with_none_author_raises(self) -> None:
        """author가 None이면 예외 발생"""
        with self.assertRaises(Exception):
            pass


class PostCommentCreateAPITestCase(APITestCase):
    """댓글 생성 API 테스트 - 성공, 인증 실패, validation 실패, 미존재 게시글"""

    def setUp(self) -> None:
        """테스트용 유저, 카테고리, 게시글, URL 생성"""
        User = get_user_model()
        self.user = User.objects.create_user(
            email="createuser@example.com",
            password="testpass",
            nickname="createuser",
            phone_number="010-5555-6666",
            gender="MALE",
            birthday="1985-02-02",
        )
        self.category = PostCategory.objects.create(name="create category")
        self.post = Post.objects.create(
            author=self.user,
            title="create post",
            content="create content",
            category=self.category,
        )
        self.create_url = reverse("posts:post-comment-create", args=[self.post.id])

    def test_comment_create_success(self) -> None:
        """정상적으로 댓글 생성 API 성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.create_url, {"content": "new comment"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("detail", response.data)

    def test_comment_create_unauthenticated(self) -> None:
        """비인증 유저는 401 반환"""
        response = self.client.post(self.create_url, {"content": "new comment"}, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.UNAUTHORIZED)

    def test_comment_create_validation_error(self) -> None:
        """content validation 실패 시 400 반환"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.create_url, {"content": "   "}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error_detail", response.data)
        self.assertIn("content", response.data["error_detail"])

    def test_comment_create_post_not_found(self) -> None:
        """존재하지 않는 게시글에 댓글 생성 시 404 반환"""
        self.client.force_authenticate(user=self.user)
        url = reverse("posts:post-comment-create", args=[999999])
        response = self.client.post(url, {"content": "new comment"}, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.COMMENT_NOT_FOUND)

    def test_comment_create_with_invalid_post_id(self) -> None:
        """잘못된 post id로 요청 시 404 반환"""
        self.client.force_authenticate(user=self.user)
        for invalid_id in [None, 0, -1]:
            url = reverse("posts:post-comment-create", args=[invalid_id if invalid_id is not None else 0])
            response = self.client.post(url, {"content": "new comment"}, format="json")
            self.assertEqual(response.status_code, 404)
            self.assertIn("error_detail", response.data)
