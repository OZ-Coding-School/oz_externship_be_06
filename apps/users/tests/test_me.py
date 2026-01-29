from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


class MeAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/accounts/me/"

        User = get_user_model()
        self.user = User.objects.create_user(
            email="me_test@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="테스터",
            nickname="tester",
            gender="MALE",
            is_active=True,
        )

        access = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_me_get_success_200(self) -> None:
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["email"], "me_test@example.com")
        self.assertEqual(data["nickname"], "tester")
        self.assertEqual(data["name"], "테스터")
        self.assertEqual(data["gender"], "M")

    def test_me_get_unauthenticated_401(self) -> None:
        self.client.credentials()

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_patch_success_200(self) -> None:
        res = self.client.patch(
            self.url,
            {"nickname": "new_nick", "name": "새이름"},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["nickname"], "new_nick")
        self.assertEqual(data["name"], "새이름")

        self.user.refresh_from_db()
        self.assertEqual(self.user.nickname, "new_nick")
        self.assertEqual(self.user.name, "새이름")

    def test_me_patch_partial_update_200(self) -> None:
        res = self.client.patch(
            self.url,
            {"nickname": "only_nick"},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["nickname"], "only_nick")
        self.assertEqual(data["name"], "테스터")

    def test_me_patch_unauthenticated_401(self) -> None:
        self.client.credentials()

        res = self.client.patch(
            self.url,
            {"nickname": "new_nick"},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
