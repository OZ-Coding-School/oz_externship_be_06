from __future__ import annotations

import json

from django.test import Client, TestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.exams.constants import ErrorMessages
from apps.users.models import User


class AdminExamPresignedUrlAPITest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="password1234",
            name="Admin",
            nickname="admin",
            phone_number="01000000000",
            gender=User.Gender.MALE,
            birthday="2000-01-01",
            role=User.Role.ADMIN,
            is_active=True,
        )
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            password="password1234",
            name="User",
            nickname="user",
            phone_number="01000000001",
            gender=User.Gender.MALE,
            birthday="2000-01-01",
            role=User.Role.USER,
            is_active=True,
        )
        self.url = "/api/v1/admin/exams/presigned-url/thumbnail/"

    def _auth_headers(self, user: User) -> dict[str, str]:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def _auth_client(self, user: User) -> Client:
        client = Client()
        client.defaults.update(self._auth_headers(user))
        return client

    def test_returns_401_when_unauthenticated(self) -> None:
        response = self.client.put(
            self.url,
            data=json.dumps({"file_name": "test.png"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.UNAUTHORIZED.value)

    def test_returns_403_when_not_staff(self) -> None:
        response = self._auth_client(self.normal_user).put(
            self.url,
            data=json.dumps({"file_name": "test.png"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.FORBIDDEN.value)
