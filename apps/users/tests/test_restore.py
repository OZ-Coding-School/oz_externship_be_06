from datetime import date, timedelta
from typing import Any
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.users.models.withdrawal import Withdrawal

User = get_user_model()


class RestoreAPITest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/accounts/restore/"

    @patch("apps.users.views.restore_view.delete_email_token")
    @patch("apps.users.views.restore_view.get_email_by_token")
    def test_restore_success(self, mock_get_email: Any, mock_delete_token: Any) -> None:
        mock_get_email.return_value = "withdrawn@example.com"
        email_token = "test-token"

        user = User.objects.create(
            email="withdrawn@example.com",
            nickname="nick",
            name="테스트",
            phone_number="01012345678",
            birthday=date(1990, 1, 1),
            gender="M",
            is_active=False,
        )
        Withdrawal.objects.create(
            user=user,
            due_date=date.today() + timedelta(days=7),
        )

        res = self.client.post(self.url, data={"email_token": email_token}, format="json")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["detail"], "계정복구가 완료되었습니다.")

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertFalse(Withdrawal.objects.filter(user=user).exists())

        mock_delete_token.assert_called_once_with(email_token)
