from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models.withdrawal import Withdrawal


class WithdrawalAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.withdrawal_url = "/api/v1/accounts/withdrawal/"

        User = get_user_model()
        self.email = "withdrawal_test@example.com"
        self.password = "Testpass123!"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="테스터",
            nickname="tester",
            gender="male",
        )

        access = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_withdrawal_success_204_and_user_inactive(self) -> None:
        res = self.client.delete(
            self.withdrawal_url,
            {"reason": "PRIVACY_CONCERN", "reason_detail": "테스트 탈퇴"},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertTrue(Withdrawal.objects.filter(user=self.user).exists())

    def test_withdrawal_invalid_reason_400(self) -> None:
        res = self.client.delete(
            self.withdrawal_url,
            {"reason": "INVALID", "reason_detail": "테스트"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_withdrawal_already_requested_400(self) -> None:
        Withdrawal.objects.create(user=self.user, reason="SERVICE_DISSATISFACTION")

        res = self.client.delete(
            self.withdrawal_url,
            {"reason": "PRIVACY_CONCERN", "reason_detail": "테스트"},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        data = res.json()
        self.assertIn("error_detail", data)

    def test_withdrawal_unauthenticated_401(self) -> None:
        self.client.credentials()

        res = self.client.delete(
            self.withdrawal_url,
            {"reason": "PRIVACY_CONCERN", "reason_detail": "테스트"},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
