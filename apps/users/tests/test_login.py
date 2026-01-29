from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import Withdrawal


class LoginAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/accounts/login/"

        User = get_user_model()
        self.email = "login_test@example.com"
        self.password = "Testpass123!"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="테스터",
            nickname="tester",
            gender="MALE",
            is_active=True,
        )

    def test_login_success_200(self) -> None:
        res = self.client.post(
            self.url,
            {"email": self.email, "password": self.password},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)

    def test_login_invalid_email_400(self) -> None:
        res = self.client.post(
            self.url,
            {"email": "wrong@example.com", "password": self.password},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_password_400(self) -> None:
        res = self.client.post(
            self.url,
            {"email": self.email, "password": "wrongpassword"},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_withdrawal_account_403(self) -> None:
        Withdrawal.objects.create(user=self.user, reason="SERVICE_DISSATISFACTION")

        res = self.client.post(
            self.url,
            {"email": self.email, "password": self.password},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        data = res.json()
        self.assertIn("error_detail", data)
        self.assertIn("expire_at", data["error_detail"])


class LogoutAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/accounts/logout/"

        User = get_user_model()
        self.user = User.objects.create_user(
            email="logout_test@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345679",
            name="테스터2",
            nickname="tester2",
            gender="MALE",
            is_active=True,
        )

        access = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_logout_success_200(self) -> None:
        res = self.client.post(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertIn("detail", data)

    def test_logout_unauthenticated_401(self) -> None:
        self.client.credentials()

        res = self.client.post(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
