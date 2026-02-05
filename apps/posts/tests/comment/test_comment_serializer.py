from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment
from apps.posts.serializers.comment_serializers import (
    PostCommentCreateSerializer,
    PostCommentListSerializer,
    PostCommentUpdateSerializer,
)

User = get_user_model()


class PostCommentSerializerTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass",
            name="테스트유저",
            nickname="testuser",
            phone_number="010-1234-5678",
            gender="MALE",
            birthday="2000-01-01",
        )
        self.category = PostCategory.objects.create(name="test category")
        self.post = Post.objects.create(
            author=self.user, title="test post", content="test content", category=self.category
        )
        self.comment = PostComment.objects.create(post=self.post, author=self.user, content="comment content")

    def test_post_comment_list_serializer_fields(self) -> None:
        data = PostCommentListSerializer(self.comment).data
        self.assertEqual(set(data.keys()), {"id", "author", "tagged_users", "content", "created_at", "updated_at"})
        self.assertEqual(data["content"], self.comment.content)

    def test_post_comment_create_serializer(self) -> None:
        serializer = PostCommentCreateSerializer(
            data={"content": "new comment"},
            context={
                "request": type("obj", (), {"user": self.user, "_request": None, "is_authenticated": True})(),
                "post": self.post,
            },
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        comment = serializer.save()
        self.assertEqual(comment.content, "new comment")
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)

    def test_post_comment_update_serializer(self) -> None:
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "updated content"},
            context={"request": type("obj", (), {"user": self.user, "_request": None, "is_authenticated": True})()},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.content, "updated content")

    def test_post_comment_create_serializer_unauthenticated(self) -> None:
        from rest_framework.exceptions import NotAuthenticated

        serializer = PostCommentCreateSerializer(
            data={"content": "new comment"},
            context={
                "request": type("obj", (), {"user": None, "is_authenticated": False})(),
                "post": self.post,
            },
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaises(NotAuthenticated):
            serializer.save()

    def test_post_comment_create_serializer_no_post(self) -> None:
        from rest_framework.exceptions import NotFound

        serializer = PostCommentCreateSerializer(
            data={"content": "new comment"},
            context={
                "request": type("obj", (), {"user": self.user, "is_authenticated": True})(),
                # "post" 미포함
            },
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaises(NotFound):
            serializer.save()

    def test_post_comment_update_serializer_authenticated_author(self) -> None:
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "updated"},
            context={"request": type("obj", (), {"user": self.user, "is_authenticated": True})()},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.content, "updated")

    def test_post_comment_update_serializer_unauthenticated(self) -> None:
        from rest_framework.exceptions import NotAuthenticated

        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "updated"},
            context={"request": type("obj", (), {"user": None, "is_authenticated": False})()},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaises(NotAuthenticated):
            serializer.save()

    def test_post_comment_update_serializer_not_author(self) -> None:
        from rest_framework.exceptions import PermissionDenied

        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "updated"},
            context={"request": type("obj", (), {"user": self.user, "is_authenticated": True})()},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        # 실제로는 self.other_user로 해야 하지만, self.other_user는 CommentServiceTests에 정의되어 있음
        # 이 테스트는 실제로는 CommentServiceTests로 옮기는 것이 더 적합함
