from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import NotAuthenticated, NotFound, PermissionDenied
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
    """PostComment Serializer 테스트"""

    def setUp(self) -> None:
        """테스트 데이터 설정"""
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.other_user = User.objects.create_user(email="other@example.com", password="testpass123")
        self.category = PostCategory.objects.create(name="테스트 카테고리", status=True)
        self.post = Post.objects.create(
            title="테스트 게시글", content="테스트 내용", author=self.user, category=self.category
        )
        self.comment = PostComment.objects.create(author=self.user, post=self.post, content="테스트 댓글")
        self.factory = APIRequestFactory()

    def test_post_comment_list_serializer(self) -> None:
        """PostCommentListSerializer 테스트"""
        serializer = PostCommentListSerializer(self.comment)
        data = serializer.data

        self.assertEqual(data["id"], self.comment.id)
        self.assertEqual(data["content"], "테스트 댓글")
        self.assertEqual(data["author"]["id"], self.user.id)
        self.assertEqual(data["author"]["nickname"], self.user.nickname)

    def test_post_comment_create_serializer_success(self) -> None:
        """PostCommentCreateSerializer 성공 테스트"""
        request = self.factory.post("/api/posts/1/comments/")
        request.user = self.user

        data = {"content": "새 댓글"}
        serializer = PostCommentCreateSerializer(data=data, context={"request": request, "post": self.post})

        self.assertTrue(serializer.is_valid())
        comment = serializer.save()

        self.assertEqual(comment.content, "새 댓글")
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)

    def test_post_comment_create_serializer_no_auth(self) -> None:
        """PostCommentCreateSerializer 인증 실패 테스트"""
        request = self.factory.post("/api/posts/1/comments/")
        request.user = None  # type: ignore[assignment]

        data = {"content": "새 댓글"}
        serializer = PostCommentCreateSerializer(data=data, context={"request": request, "post": self.post})

        self.assertTrue(serializer.is_valid())
        with self.assertRaises(NotAuthenticated):
            serializer.save()

    def test_post_comment_create_serializer_no_post(self) -> None:
        """PostCommentCreateSerializer 게시글 없음 테스트"""
        request = self.factory.post("/api/posts/1/comments/")
        request.user = self.user

        data = {"content": "새 댓글"}
        serializer = PostCommentCreateSerializer(data=data, context={"request": request})

        self.assertTrue(serializer.is_valid())
        with self.assertRaises(Exception):  # ValidationError 또는 NotFound
            serializer.save()

    def test_post_comment_update_serializer_success(self) -> None:
        """PostCommentUpdateSerializer 성공 테스트"""
        request = self.factory.put(f"/api/posts/1/comments/{self.comment.id}/")
        request.user = self.user

        data = {"content": "수정된 댓글"}
        serializer = PostCommentUpdateSerializer(instance=self.comment, data=data, context={"request": request})

        self.assertTrue(serializer.is_valid())
        updated_comment = serializer.save()

        self.assertEqual(updated_comment.content, "수정된 댓글")
        self.assertEqual(updated_comment.author, self.user)

    def test_post_comment_update_serializer_permission_denied(self) -> None:
        """PostCommentUpdateSerializer 권한 없음 테스트"""
        request = self.factory.put(f"/api/posts/1/comments/{self.comment.id}/")
        request.user = self.other_user

        data = {"content": "수정된 댓글"}
        serializer = PostCommentUpdateSerializer(instance=self.comment, data=data, context={"request": request})

        with self.assertRaises(PermissionDenied):
            serializer.is_valid(raise_exception=True)

    def test_post_comment_update_serializer_no_auth(self) -> None:
        """PostCommentUpdateSerializer 인증 실패 테스트"""
        request = self.factory.put(f"/api/posts/1/comments/{self.comment.id}/")
        request.user = None  # type: ignore[assignment]

        data = {"content": "수정된 댓글"}
        serializer = PostCommentUpdateSerializer(instance=self.comment, data=data, context={"request": request})

        with self.assertRaises(NotAuthenticated):
            serializer.is_valid(raise_exception=True)
