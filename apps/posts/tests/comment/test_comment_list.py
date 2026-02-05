from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment
from apps.posts.serializers.comment_serializers import PostCommentListSerializer
from apps.posts.services.comment.comment_list_services import list_comments


class PostCommentListSerializerTests(TestCase):
    """댓글 리스트 시리얼라이저 테스트"""

    def setUp(self) -> None:
        """테스트용 유저, 카테고리, 게시글, 댓글 생성"""
        User = get_user_model()
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

    def test_list_serializer_tagged_users_field(self) -> None:
        """tagged_users 필드가 리스트로 포함되는지 확인"""
        data = PostCommentListSerializer(self.comment).data
        self.assertIn("tagged_users", data)
        self.assertIsInstance(data["tagged_users"], list)

    def test_post_comment_list_serializer_fields(self) -> None:
        """필드 값이 정상적으로 매핑되는지 확인"""
        data = PostCommentListSerializer(self.comment).data
        self.assertEqual(set(data.keys()), {"id", "author", "tagged_users", "content", "created_at", "updated_at"})
        self.assertEqual(data["content"], self.comment.content)


class CommentListServiceTests(TestCase):
    """댓글 리스트 서비스 테스트"""

    def setUp(self) -> None:
        """테스트용 유저, 카테고리, 게시글, 댓글 생성"""
        User = get_user_model()
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

    def test_list_comments_returns_comments_for_post(self) -> None:
        """게시글 id로 댓글 리스트 반환"""
        # 여러 댓글 생성
        comment2 = PostComment.objects.create(post=self.post, author=self.user, content="comment 2")
        comments = list(list_comments(self.post.id))
        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0].post, self.post)
        self.assertEqual(comments[1].post, self.post)
        contents = [c.content for c in comments]
        self.assertIn("comment content", contents)
        self.assertIn("comment 2", contents)

    def test_list_comments_empty_for_no_comments(self) -> None:
        """댓글이 없는 게시글 id로 빈 리스트 반환"""
        new_post = Post.objects.create(
            author=self.user,
            title="no comment post",
            content="no comment content",
            category=self.category,
        )
        comments = list(list_comments(new_post.id))
        self.assertEqual(comments, [])


class PostCommentDetailAPITestCase(APITestCase):
    """댓글 상세 조회 API 테스트 - 정상 조회, 댓글 미존재 시 예외"""

    COMMENT_NOT_FOUND_MSG = CommentErrorMessage.COMMENT_NOT_FOUND

    def setUp(self) -> None:
        """테스트용 유저, 카테고리, 게시글, 인증 설정"""
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

    def test_comment_detail_safe_methods_permission(self) -> None:
        """작성자/비작성자/비로그인 모두 GET 가능"""
        # 작성자
        comment = PostComment.objects.create(
            author=self.user,
            post=self.post,
            content="작성자 댓글",
        )
        url = reverse("posts:post-comment-rud", args=[self.post.id, comment.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # 비작성자
        User = get_user_model()
        other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="testpass",
            nickname="otheruser",
            phone_number="010-0000-0000",
            gender="FEMALE",
            birthday="1999-09-09",
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # 비로그인
        self.client.force_authenticate(user=None)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_comment_detail_success(self) -> None:
        """댓글 상세 조회 성공"""
        url = reverse("posts:post-comment-rud", args=[self.post.id, 1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.data)
        self.assertIn("content", response.data)
        self.assertEqual(response.data["id"], 1)

    def test_comment_detail_not_found(self) -> None:
        """존재하지 않는 댓글 조회 시 404 반환"""
        url = reverse("posts:post-comment-rud", args=[self.post.id, 999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], self.COMMENT_NOT_FOUND_MSG)
