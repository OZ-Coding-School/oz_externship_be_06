from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.test import APITestCase

from apps.posts.models import PostCategory


class PostCategoryTests(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("category-list")
        PostCategory.objects.create(name="공지사항", status=True)
        PostCategory.objects.create(name="비활성카테고리", status=False)

    def test_get_categories_success(self) -> None:
        """활성화된 카테고리만 잘 가져오는지 테스트"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "공지사항")

    def test_get_categories_error_handling(self) -> None:
        """의도적으로 에러를 발생시켜 handle_exception 로직을 실행"""
        with patch("apps.posts.views.post_category_views.PostCategory.objects.filter") as mocked_filter:

            mocked_filter.side_effect = APIException("데이터베이스 연결 오류")

            response = self.client.get(self.url)

            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn("error_detail", response.data)
