from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory

from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment
from apps.posts.serializers.post_comment import (
    PostCommentCreateSerializer,
    PostCommentListSerializer,
    PostCommentUpdateSerializer,
)

User = get_user_model()


class PostCommentSerializerTestCase(TestCase):
    """PostComment Serializer 테스트 (옵션 1: 인증은 view/permission 레이어에서만)"""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            name="테스트유저",
            nickname="테스터",
            phone_number="01012345678",
            gender="MALE",
            birthday="1990-01-01",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
            name="다른유저",
            nickname="다른이",
            phone_number="01087654321",
            gender="FEMALE",
            birthday="1995-05-05",
        )
        self.category = PostCategory.objects.create(name="테스트 카테고리", status=True)
        self.post = Post.objects.create(
            title="테스트 게시글",
            content="테스트 내용",
            author=self.user,
            category=self.category,
        )
        self.comment = PostComment.objects.create(author=self.user, post=self.post, content="테스트 댓글")
        self.factory = APIRequestFactory()

    def test_post_comment_list_serializer(self) -> None:
        """PostCommentListSerializer 기본 필드/author 포함 확인"""
        serializer = PostCommentListSerializer(self.comment)
        data = serializer.data

        self.assertEqual(data["id"], self.comment.id)
        self.assertEqual(data["content"], "테스트 댓글")
        self.assertEqual(data["author"]["id"], self.user.id)
        self.assertEqual(data["author"]["nickname"], self.user.nickname)
        self.assertIn("tagged_users", data)

    def test_post_comment_create_serializer_success(self) -> None:
        """PostCommentCreateSerializer 성공: content만 검증 + create 동작"""
        request = self.factory.post("/api/posts/1/comments/")
        request.user = self.user

        serializer = PostCommentCreateSerializer(
            data={"content": "새 댓글"},
            context={"request": request, "post": self.post},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        comment = serializer.save()
        self.assertEqual(comment.content, "새 댓글")
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)

    def test_post_comment_create_serializer_missing_author_save_fails(self) -> None:
        """PostCommentCreateSerializer - author 없음: 옵션1 기준으로 is_valid는 통과 가능, save에서 실패"""
        request = self.factory.post("/api/posts/1/comments/")
        request.user = None  # type: ignore[assignment]

        serializer = PostCommentCreateSerializer(
            data={"content": "새 댓글"},
            context={"request": request, "post": self.post},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        with self.assertRaises(serializers.ValidationError):
            serializer.save()

    def test_post_comment_create_serializer_missing_post_save_fails(self) -> None:
        """PostCommentCreateSerializer - post 컨텍스트 없음: save에서 실패"""
        request = self.factory.post("/api/posts/1/comments/")
        request.user = self.user

        serializer = PostCommentCreateSerializer(
            data={"content": "새 댓글"},
            context={"request": request},  # post 없음
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        with self.assertRaises(serializers.ValidationError):
            serializer.save()

    def test_post_comment_update_serializer_success(self) -> None:
        """PostCommentUpdateSerializer 성공: 작성자만 수정 가능"""
        request = self.factory.put(f"/api/posts/1/comments/{self.comment.id}/")
        request.user = self.user

        serializer = PostCommentUpdateSerializer(
            instance=self.comment,
            data={"content": "수정된 댓글"},
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        updated = serializer.save()
        self.assertEqual(updated.content, "수정된 댓글")
        self.assertEqual(updated.author, self.user)

    def test_post_comment_update_serializer_permission_denied(self) -> None:
        """PostCommentUpdateSerializer - 권한 없음(작성자 아님)"""
        request = self.factory.put(f"/api/posts/1/comments/{self.comment.id}/")
        request.user = self.other_user

        serializer = PostCommentUpdateSerializer(
            instance=self.comment,
            data={"content": "수정된 댓글"},
            context={"request": request},
        )
        with self.assertRaises(PermissionDenied):
            serializer.is_valid(raise_exception=True)
