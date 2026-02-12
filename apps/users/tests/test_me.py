from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.models.withdrawal import Withdrawal


class MeAPITests(TestCase):
    client: APIClient

    url: str
    user: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = "/api/v1/accounts/me/"

        cls.user = User.objects.create_user(
            email="me_test@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="테스터",
            nickname="tester",
            gender="MALE",
            is_active=True,
        )

    def setUp(self) -> None:
        self.client = APIClient()
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

    def test_withdrawal_success_204_and_user_inactive(self) -> None:
        res = self.client.delete(
            "/api/v1/accounts/withdrawal/",
            {"reason": "PRIVACY_CONCERN", "reason_detail": "테스트 탈퇴"},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertTrue(Withdrawal.objects.filter(user=self.user).exists())

    def test_withdrawal_invalid_reason_400(self) -> None:
        res = self.client.delete(
            "/api/v1/accounts/withdrawal/",
            {"reason": "INVALID", "reason_detail": "테스트"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_withdrawal_already_requested_400(self) -> None:
        Withdrawal.objects.create(
            user=self.user,
            reason="SERVICE_DISSATISFACTION",
            reason_detail="이미 탈퇴 신청된 상태",
        )

        res = self.client.delete(
            "/api/v1/accounts/withdrawal/",
            {"reason": "PRIVACY_CONCERN", "reason_detail": "테스트"},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        data = res.json()
        self.assertIn("error_detail", data)

    def test_withdrawal_unauthenticated_401(self) -> None:
        self.client.credentials()

        res = self.client.delete(
            "/api/v1/accounts/withdrawal/",
            {"reason": "PRIVACY_CONCERN", "reason_detail": "테스트"},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
