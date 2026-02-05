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
        # 테스트용 유저, 카테고리, 게시글, 댓글을 생성합니다.
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

    def test_create_serializer_empty_content(self) -> None:
        # 댓글 내용이 비어있을 때 ValidationError가 발생하는지 테스트
        serializer = PostCommentCreateSerializer(
            data={"content": "   "},
            context={"request": type("obj", (), {"user": self.user, "is_authenticated": True})(), "post": self.post},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_create_serializer_too_long_content(self) -> None:
        # 댓글 내용이 최대 길이를 초과할 때 ValidationError가 발생하는지 테스트
        long_content = "a" * 501
        serializer = PostCommentCreateSerializer(
            data={"content": long_content},
            context={"request": type("obj", (), {"user": self.user, "is_authenticated": True})(), "post": self.post},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_update_serializer_empty_content(self) -> None:
        # 댓글 수정 시 내용이 비어있을 때 ValidationError가 발생하는지 테스트
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "   "},
            context={"request": type("obj", (), {"user": self.user, "is_authenticated": True})()},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_update_serializer_too_long_content(self) -> None:
        # 댓글 수정 시 내용이 최대 길이를 초과할 때 ValidationError가 발생하는지 테스트
        long_content = "a" * 501
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": long_content},
            context={"request": type("obj", (), {"user": self.user, "is_authenticated": True})()},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_list_serializer_tagged_users_field(self) -> None:
        # 댓글 목록 시리얼라이저에서 tagged_users 필드가 항상 포함되는지 테스트
        data = PostCommentListSerializer(self.comment).data
        self.assertIn("tagged_users", data)
        self.assertIsInstance(data["tagged_users"], list)

    def test_post_comment_list_serializer_fields(self) -> None:
        # 댓글 목록 시리얼라이저 필드와 값 검증
        data = PostCommentListSerializer(self.comment).data
        self.assertEqual(set(data.keys()), {"id", "author", "tagged_users", "content", "created_at", "updated_at"})
        self.assertEqual(data["content"], self.comment.content)

    def test_post_comment_create_serializer(self) -> None:
        # 댓글 생성 시리얼라이저 정상 동작 검증
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
        # 댓글 수정 시리얼라이저 정상 동작 검증
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "updated content"},
            context={"request": type("obj", (), {"user": self.user, "_request": None, "is_authenticated": True})()},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.content, "updated content")

    def test_post_comment_create_serializer_unauthenticated(self) -> None:
        # 인증되지 않은 유저가 댓글 생성 시 예외 발생 검증
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
        # post가 없는 경우 예외 발생 검증
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

    def test_post_comment_create_serializer_no_request(self) -> None:
        # context에 request가 없는 경우 예외 발생 검증
        from rest_framework.exceptions import NotAuthenticated

        serializer = PostCommentCreateSerializer(
            data={"content": "new comment"},
            context={"post": self.post},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaises(NotAuthenticated):
            serializer.save()

    def test_post_comment_create_serializer_wrong_post_type(self) -> None:
        # context의 post가 Post 타입이 아닌 경우 예외 발생 검증
        from rest_framework.exceptions import NotFound

        serializer = PostCommentCreateSerializer(
            data={"content": "new comment"},
            context={"request": type("obj", (), {"user": self.user, "is_authenticated": True})(), "post": "not_a_post"},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaises(NotFound):
            serializer.save()

    def test_post_comment_update_serializer_authenticated_author(self) -> None:
        # 댓글 작성자가 인증된 경우 정상적으로 수정되는지 검증
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "updated"},
            context={"request": type("obj", (), {"user": self.user, "is_authenticated": True})()},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.content, "updated")

    def test_post_comment_update_serializer_unauthenticated(self) -> None:
        # 인증되지 않은 유저가 댓글 수정 시 예외 발생 검증
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
        # 댓글 작성자가 아닌 경우 수정 시 PermissionDenied가 발생하는지 테스트합니다.
        from rest_framework.exceptions import PermissionDenied

        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "updated"},
            context={"request": type("obj", (), {"user": self.user, "is_authenticated": True})()},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
