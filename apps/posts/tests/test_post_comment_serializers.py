from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment
from apps.posts.serializers.post_comment import (
    PostCommentCreateSerializer,
    PostCommentListSerializer,
    PostCommentUpdateSerializer,
)

User = get_user_model()


class PostCommentSerializerTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="testpass")
        self.post = Post.objects.create(author=self.user, title="test post", content="test content")
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
