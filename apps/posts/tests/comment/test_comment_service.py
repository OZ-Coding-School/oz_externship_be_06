from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment
from apps.posts.serializers.comment_serializers import PostCommentUpdateSerializer

User = get_user_model()


class CommentServiceTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass",
            nickname="testuser",
            phone_number="010-1234-5678",
            gender="MALE",
            birthday="2000-01-01",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass",
            nickname="otheruser",
            phone_number="010-0000-0000",
            gender="FEMALE",
            birthday="2001-01-01",
        )
        self.category = PostCategory.objects.create(name="test category")
        self.post = Post.objects.create(
            author=self.user, title="test post", content="test content", category=self.category
        )
        self.comment = PostComment.objects.create(post=self.post, author=self.user, content="comment content")

    def test_post_comment_update_serializer_not_author(self) -> None:
        from rest_framework.exceptions import PermissionDenied

        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "updated"},
            context={"request": type("obj", (), {"user": self.other_user, "is_authenticated": True})()},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaises(PermissionDenied):
            serializer.save()
