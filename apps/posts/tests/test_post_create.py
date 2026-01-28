from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.posts.models import Post, PostCategory

User = get_user_model()


class PostCreateAPITest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            nickname="tester",
            name="테스터",
            birthday="2002-04-22",
            gender="M",
        )
        self.category = PostCategory.objects.create(name="자유게시판", status=True)
        self.url = reverse("post-list")

    def test_create_post_success(self) -> None:
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "테스트 제목",
            "content": "테스트 내용",
            "category_id": self.category.id,
            "is_notice": False,
            "is_visible": True,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "게시글이 성공적으로 등록되었습니다.")
        self.assertTrue("pk" in response.data)

    def test_create_post_bad_request(self) -> None:
        self.client.force_authenticate(user=self.user)
        data = {"content": "제목이 없는 데이터", "category_id": self.category.id}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)
        self.assertIn("title", response.data["error_detail"])
        self.assertIsInstance(response.data["error_detail"]["title"], list)

    def test_create_post_unauthorized(self) -> None:
        data = {"title": "로그인 안함", "content": "내용", "category_id": self.category.id}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error_detail", response.data)
        self.assertIsInstance(response.data["error_detail"], str)

    def test_retrieve_post_increases_view_count(self) -> None:

        post = Post.objects.create(title="상세보기 테스트", content="내용", author=self.user, category=self.category)
        url = reverse("post-detail", kwargs={"pk": post.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.view_count, 1)

    def test_retrieve_post_success(self) -> None:
        post = Post.objects.create(title="조회 테스트", content="내용", author=self.user, category=self.category)
        url = reverse("post-detail", kwargs={"pk": post.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.view_count, 1)

    def test_update_post_by_non_author(self) -> None:
        other_user = User.objects.create_user(
            email="other@test.com", password="pw", nickname="other", name="다른이", birthday="2000-01-01", gender="F"
        )
        post = Post.objects.create(title="내 글", content="내용", author=self.user, category=self.category)
        url = reverse("post-detail", kwargs={"pk": post.pk})

        self.client.force_authenticate(user=other_user)
        response = self.client.put(url, {"title": "해킹"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_success(self) -> None:
        post = Post.objects.create(title="삭제글", content="내용", author=self.user, category=self.category)
        url = reverse("post-detail", kwargs={"pk": post.pk})

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())
