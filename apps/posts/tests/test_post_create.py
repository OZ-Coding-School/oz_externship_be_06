from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.posts.models import PostCategory
from apps.users.models import User
from apps.posts.constants.post_const import PostSuccessMessage, PostErrorMessage

class PostCreateTest(APITestCase):
    def setUp(self):
        # 유저 및 카테고리 준비
        self.user = User.objects.create_user(
            email="test@oz.com",
            password="pw",
            name="테스터",
            nickname="테스트닉네임",
            phone_number="010-1234-5678",
            gender="MALE",
            birthday="2002-04-22",
        )
        self.category = PostCategory.objects.create(name="테스트카테고리")
        self.url = reverse('post-create')
        # [중요] 여기서 force_authenticate를 제거합니다.

    def test_create_post_201_success(self):
        """201 Created 확인"""
        # 성공 케이스에서만 명시적으로 인증
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "테스트 제목",
            "content": "테스트 내용",
            "category_id": self.category.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], PostSuccessMessage.POST_CREATE_SUCCESS)

    def test_create_post_400_bad_request(self):
        """400 Bad Request 확인"""
        self.client.force_authenticate(user=self.user)
        # title 누락
        data = {
            "content": "내용만 있음",
            "category_id": self.category.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    def test_create_post_401_unauthorized(self):
        self.client.force_authenticate(user=None) # 인증 해제

        data = {"title": "test", "content": "test", "category_id": self.category.id}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # 이제 string='None'이 아닌 실제 메시지가 비교될 것입니다.
        self.assertEqual(response.data["error_detail"], PostErrorMessage.UNAUTHORIZED)