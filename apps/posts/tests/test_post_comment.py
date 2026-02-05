from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.posts.constants.post_const import PostErrorMessage
from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment
from apps.posts.serializers.post_comment import (
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

    # 댓글 목록 시리얼라이저 필드 및 값 검증
    def test_post_comment_list_serializer_fields(self) -> None:
        data = PostCommentListSerializer(self.comment).data
        self.assertEqual(set(data.keys()), {"id", "author", "tagged_users", "content", "created_at", "updated_at"})
        self.assertEqual(data["content"], self.comment.content)

    # 댓글 생성 시리얼라이저 동작 및 저장값 검증
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

    # 댓글 수정 시리얼라이저 동작 및 저장값 검증
    def test_post_comment_update_serializer(self) -> None:
        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "updated content"},
            context={"request": type("obj", (), {"user": self.user, "_request": None, "is_authenticated": True})()},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.content, "updated content")

        # 인증되지 않은 사용자가 댓글 생성 시 예외 발생 검증
        def test_post_comment_create_serializer_unauthenticated(self):
            serializer = PostCommentCreateSerializer(
                data={"content": "new comment"},
                context={
                    "request": type("obj", (), {"user": None, "is_authenticated": False})(),
                    "post": self.post,
                },
            )
            self.assertTrue(serializer.is_valid(), serializer.errors)
            from rest_framework.exceptions import NotAuthenticated
            with self.assertRaises(NotAuthenticated):
                serializer.save()

        # post 객체 없이 댓글 생성 시 예외 발생 검증
        def test_post_comment_create_serializer_no_post(self):
            serializer = PostCommentCreateSerializer(
                data={"content": "new comment"},
                context={
                    "request": type("obj", (), {"user": self.user, "is_authenticated": True})(),
                    # "post" 미포함
                },
            )
            self.assertTrue(serializer.is_valid(), serializer.errors)
            from rest_framework.exceptions import NotFound
            with self.assertRaises(NotFound):
                serializer.save()


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

    # 인증된 사용자가 정상적으로 댓글 생성 검증
    def test_validate_comment_create_authenticated(self) -> None:
        from apps.posts.services import comment_services

        context = {"request": type("obj", (), {"user": self.user, "is_authenticated": True})(), "post": self.post}
        attrs = {"content": "test"}
        result = comment_services.validate_comment_create(attrs, context)
        self.assertEqual(result, attrs)

    # 인증되지 않은 사용자가 댓글 생성 시 예외 발생 검증
    def test_validate_comment_create_unauthenticated(self) -> None:
        from rest_framework.exceptions import NotAuthenticated

        from apps.posts.services import comment_services

        context = {"request": type("obj", (), {"user": None, "is_authenticated": False})(), "post": self.post}
        attrs = {"content": "test"}
        with self.assertRaises(NotAuthenticated):
            comment_services.validate_comment_create(attrs, context)

    # post 객체 없이 댓글 생성 시 예외 발생 검증
    def test_validate_comment_create_no_post(self) -> None:
        from rest_framework.exceptions import NotFound

        from apps.posts.services import comment_services

        context = {"request": type("obj", (), {"user": self.user, "is_authenticated": True})()}
        attrs = {"content": "test"}
        with self.assertRaises(NotFound):
            comment_services.validate_comment_create(attrs, context)

    # 인증된 작성자가 본인 댓글 수정 가능 검증
    def test_validate_comment_update_authenticated_author(self) -> None:
        from apps.posts.services import comment_services

        context = {"request": type("obj", (), {"user": self.user, "is_authenticated": True})()}
        attrs = {"content": "updated"}
        result = comment_services.validate_comment_update(attrs, context, self.comment)
        self.assertEqual(result, attrs)

    # 인증되지 않은 사용자가 댓글 수정 시 예외 발생 검증
    def test_validate_comment_update_unauthenticated(self) -> None:
        from rest_framework.exceptions import NotAuthenticated

        from apps.posts.services import comment_services

        context = {"request": type("obj", (), {"user": None, "is_authenticated": False})()}
        attrs = {"content": "updated"}
        with self.assertRaises(NotAuthenticated):
            comment_services.validate_comment_update(attrs, context, self.comment)

    # 작성자가 아닌 사용자가 댓글 수정 시 예외 발생 검증
    def test_validate_comment_update_not_author(self) -> None:
        from rest_framework.exceptions import PermissionDenied

        from apps.posts.services import comment_services

        context = {"request": type("obj", (), {"user": self.other_user, "is_authenticated": True})()}
        attrs = {"content": "updated"}
        with self.assertRaises(PermissionDenied):
            comment_services.validate_comment_update(attrs, context, self.comment)


class PostCommentDetailAPITestCase(APITestCase):
    COMMENT_NOT_FOUND_MSG = PostErrorMessage.COMMENT_NOT_FOUND

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass",
            nickname="testuser",
            phone_number="010-1234-5678",
            gender="MALE",
            birthday="2000-01-01",
        )
        self.category = PostCategory.objects.create(name="test category")
        self.post = Post.objects.create(
            author=self.user,
            title="test post",
            content="test content",
            category=self.category,
        )
        self.client.force_authenticate(user=self.user)

    # 댓글 상세 조회 성공 케이스 검증
    def test_comment_detail_success(self) -> None:
        url = reverse("posts:post-comment-rud", args=[self.post.id, 1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.data)
        self.assertIn("content", response.data)
        self.assertEqual(response.data["id"], 1)

    # 존재하지 않는 댓글 조회 시 404 반환 검증
    def test_comment_detail_not_found(self) -> None:
        url = reverse("posts:post-comment-rud", args=[self.post.id, 999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], self.COMMENT_NOT_FOUND_MSG)

    page_size = 10
