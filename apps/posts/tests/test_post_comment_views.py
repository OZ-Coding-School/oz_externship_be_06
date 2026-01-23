from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment

User = get_user_model()


class PostCommentAPITestCase(TestCase):
    """PostComment API 뷰 테스트 (명세 준수 URL)"""

    def setUp(self) -> None:
        self.client = APIClient()

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

    def test_comment_list_get(self) -> None:
        """댓글 목록 조회 테스트 (pagination: count/next/previous/results)"""
        url = f"/api/v1/posts/{self.post.id}/comments/?page=1&page_size=10"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data: Any = getattr(response, "data", None)
        self.assertIsInstance(data, dict)

        self.assertIn("count", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)
        self.assertIn("results", data)
        self.assertIsInstance(data["results"], list)

        if data["results"]:
            first = data["results"][0]
            self.assertIn("id", first)
            self.assertIn("author", first)
            self.assertIn("content", first)
            self.assertIn("tagged_users", first)

    def test_comment_list_get_post_not_found(self) -> None:
        """댓글 목록 조회 - 게시글 없음(404)"""
        url = "/api/v1/posts/999999/comments/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data: Any = getattr(response, "data", None)
        self.assertTrue(
            ("detail" in data and data["detail"] == "해당 게시글을 찾을 수 없습니다.")
            or ("error_detail" in data and data["error_detail"] == "해당 게시글을 찾을 수 없습니다.")
        )

    def test_comment_create_post(self) -> None:
        """댓글 생성 테스트 (201 + detail 메시지)"""
        self.client.force_authenticate(user=self.user)  # type: ignore[attr-defined]

        url = f"/api/v1/posts/{self.post.id}/comments/"
        payload = {"content": "새 댓글"}
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body: Any = getattr(response, "data", None)
        self.assertEqual(body, {"detail": "댓글이 등록되었습니다."})

        self.assertTrue(PostComment.objects.filter(post=self.post, author=self.user, content="새 댓글").exists())

    def test_comment_create_post_unauthorized(self) -> None:
        """댓글 생성 - 인증 없음(401)"""
        url = f"/api/v1/posts/{self.post.id}/comments/"
        payload = {"content": "새 댓글"}
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_create_post_not_found(self) -> None:
        """댓글 생성 - 게시글 없음(404)"""
        self.client.force_authenticate(user=self.user)  # type: ignore[attr-defined]

        url = "/api/v1/posts/999999/comments/"
        payload = {"content": "새 댓글"}
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data: Any = getattr(response, "data", None)
        self.assertTrue(
            ("detail" in data and data["detail"] == "해당 게시글을 찾을 수 없습니다.")
            or ("error_detail" in data and data["error_detail"] == "해당 게시글을 찾을 수 없습니다.")
        )

    def test_comment_retrieve_get_mock(self) -> None:
        """댓글 상세 조회 테스트 (mock)"""
        self.client.force_authenticate(user=self.user)  # type: ignore[attr-defined]

        url = f"/api/v1/posts/{self.post.id}/comments/{self.comment.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data: Any = getattr(response, "data", None)
        self.assertIsInstance(data, dict)
        self.assertIn("content", data)

    def test_comment_update_put_mock(self) -> None:
        """댓글 수정 테스트 (mock: 200 + id/content/updated_at)"""
        self.client.force_authenticate(user=self.user)  # type: ignore[attr-defined]

        url = f"/api/v1/posts/{self.post.id}/comments/{self.comment.id}/"
        payload = {"content": "수정된 댓글"}
        response = self.client.put(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data: Any = getattr(response, "data", None)
        self.assertIsInstance(data, dict)

        self.assertEqual(data["id"], self.comment.id)
        self.assertEqual(data["content"], "수정된 댓글")
        self.assertIn("updated_at", data)

    def test_comment_update_put_permission_denied_mock(self) -> None:
        """댓글 수정 - 권한 없음(403) (mock: serializer 권한 체크)"""
        self.client.force_authenticate(user=self.other_user)  # type: ignore[attr-defined]

        url = f"/api/v1/posts/{self.post.id}/comments/{self.comment.id}/"
        payload = {"content": "수정된 댓글"}
        response = self.client.put(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_update_put_not_found_mock(self) -> None:
        """댓글 수정 - 댓글 없음(404) (mock 규칙: comment_id<=0)"""
        self.client.force_authenticate(user=self.user)  # type: ignore[attr-defined]

        url = f"/api/v1/posts/{self.post.id}/comments/0/"
        payload = {"content": "수정된 댓글"}
        response = self.client.put(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data: Any = getattr(response, "data", None)
        self.assertTrue(
            ("detail" in data and data["detail"] == "해당 댓글을 찾을 수 없습니다.")
            or ("error_detail" in data and data["error_detail"] == "해당 댓글을 찾을 수 없습니다.")
        )

    def test_comment_delete_mock(self) -> None:
        """댓글 삭제 테스트 (mock: 200 + detail 메시지)"""
        self.client.force_authenticate(user=self.user)  # type: ignore[attr-defined]

        url = f"/api/v1/posts/{self.post.id}/comments/{self.comment.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body: Any = getattr(response, "data", None)
        self.assertEqual(body, {"detail": "댓글이 삭제되었습니다."})

    def test_comment_delete_not_found_mock(self) -> None:
        """댓글 삭제 - 댓글 없음(404) (mock 규칙: comment_id<=0)"""
        self.client.force_authenticate(user=self.user)  # type: ignore[attr-defined]

        url = f"/api/v1/posts/{self.post.id}/comments/0/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data: Any = getattr(response, "data", None)
        self.assertTrue(
            ("detail" in data and data["detail"] == "해당 댓글을 찾을 수 없습니다.")
            or ("error_detail" in data and data["error_detail"] == "해당 댓글을 찾을 수 없습니다.")
        )
