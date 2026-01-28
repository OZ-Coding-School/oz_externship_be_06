from typing import Any

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.posts.models.post_category import PostCategory


class PostCategoryAPITestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_category_list_get(self) -> None:
        active = PostCategory.objects.create(name="전체 게시판", status=True)
        PostCategory.objects.create(name="비활성", status=False)

        response = self.client.get("/api/v1/posts/categories/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data: Any = getattr(response, "data", None)
        self.assertIsInstance(data, list)
        self.assertTrue(any(item.get("id") == active.id and item.get("name") == "전체 게시판" for item in data))
        self.assertFalse(any(item.get("name") == "비활성" for item in data))
