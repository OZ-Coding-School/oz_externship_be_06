from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment
from apps.posts.models.post_comment_tags import PostCommentTag
from apps.posts.serializers.comment_serializers import PostCommentListSerializer


class CommentListSerializerTests(TestCase):
    """댓글 리스트 시리얼라이저 테스트"""

    def setUp(self) -> None:
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
            author=self.user,
            title="test post",
            content="test content",
            category=self.category,
        )

        self.comment = PostComment.objects.create(
            post=self.post,
            author=self.user,
            content="comment content",
        )

    def test_post_comment_list_serializer_fields(self) -> None:
        """기본 필드 매핑 검증 (태그 없는 케이스)"""
        data = PostCommentListSerializer(self.comment).data

        self.assertEqual(
            set(data.keys()),
            {"id", "author", "tagged_users", "content", "created_at", "updated_at"},
        )
        self.assertEqual(data["content"], self.comment.content)
        self.assertIsInstance(data["tagged_users"], list)
        self.assertEqual(len(data["tagged_users"]), 0)

    def test_list_serializer_with_one_tagged_user(self) -> None:
        """태그된 유저가 있을 때 id/nickname이 정상 직렬화되는지 검증"""
        TaggedUser = get_user_model().objects.create_user(
            email="tagged@example.com",
            password="testpass",
            name="태그유저",
            nickname="taggedusr",
            phone_number="010-0000-0000",
            gender="MALE",
            birthday="2000-01-02",
        )

        PostCommentTag.objects.create(
            comment=self.comment,
            tagged_user=TaggedUser,
        )

        data = PostCommentListSerializer(self.comment).data

        self.assertEqual(len(data["tagged_users"]), 1)
        self.assertEqual(data["tagged_users"][0]["id"], TaggedUser.id)
        self.assertEqual(data["tagged_users"][0]["nickname"], TaggedUser.nickname)


class PostCommentListAPITestCase(APITestCase):
    """댓글 목록 조회 API 테스트"""

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            email="apilistuser@example.com",
            password="testpass",
            nickname="apilistusr",
            phone_number="010-9999-8888",
            gender="MALE",
            birthday="1995-05-05",
        )
        self.category = PostCategory.objects.create(name="apilist category")
        self.post = Post.objects.create(
            author=self.user,
            title="apilist post",
            content="apilist content",
            category=self.category,
        )
        self.list_url = reverse("posts:post-comment-list", args=[self.post.id])

    def test_comment_list_success(self) -> None:
        """정상적으로 댓글 목록 조회 성공 (200)"""
        PostComment.objects.create(post=self.post, author=self.user, content="comment1")
        PostComment.objects.create(post=self.post, author=self.user, content="comment2")

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)

        contents = [c["content"] for c in response.data["results"]]
        self.assertIn("comment1", contents)
        self.assertIn("comment2", contents)

    def test_comment_list_success_with_pagination_params(self) -> None:
        """
        page/page_size 파라미터를 넣어서 list view 내부 분기(페이지네이션 경로)를 더 태움
        """
        PostComment.objects.create(post=self.post, author=self.user, content="p1")
        PostComment.objects.create(post=self.post, author=self.user, content="p2")
        PostComment.objects.create(post=self.post, author=self.user, content="p3")

        response = self.client.get(self.list_url, {"page": 1, "page_size": 2})
        self.assertEqual(response.status_code, 200)

        self.assertIn("results", response.data)
        self.assertLessEqual(len(response.data["results"]), 2)

    def test_comment_list_includes_tagged_users(self) -> None:
        """
        tagged_users가 API 응답에도 실제로 포함되는지
        (serializer TaggedUser 경로 + view/list 경로 같이 커버)
        """
        comment = PostComment.objects.create(post=self.post, author=self.user, content="tagged-target")

        tagged_user = get_user_model().objects.create_user(
            email="tagged_api@example.com",
            password="testpass",
            nickname="taggedapi",
            phone_number="010-0000-0000",
            gender="MALE",
            birthday="1999-01-01",
        )
        PostCommentTag.objects.create(comment=comment, tagged_user=tagged_user)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

        """해당 댓글을 찾아서 tagged_users 확인"""
        target = None
        for row in response.data["results"]:
            if row["content"] == "tagged-target":
                target = row
                break
        self.assertIsNotNone(target)
        assert target is not None  # for mypy
        self.assertIn("tagged_users", target)
        self.assertEqual(target["tagged_users"][0]["id"], tagged_user.id)
        self.assertEqual(target["tagged_users"][0]["nickname"], tagged_user.nickname)
