from typing import Any
from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.users.utils.redis_utils import save_email_code


class SendEmailVerificationAPIViewTest(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/accounts/verification/send-email/"

    @patch("apps.users.views.email_verification_view.send_mail")
    def test_send_email_verification_success(self, mock_send_mail: MagicMock) -> None:
        mock_send_mail.return_value = 1
        data: dict[str, Any] = {"email": "test@example.com"}
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        mock_send_mail.assert_called_once()

    def test_send_email_verification_invalid_email(self) -> None:
        data: dict[str, Any] = {"email": "invalid-email"}
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_send_email_verification_missing_email(self) -> None:
        data: dict[str, Any] = {}
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    @patch("apps.users.views.email_verification_view.send_mail")
    def test_send_email_verification_fail(self, mock_send_mail: MagicMock) -> None:
        mock_send_mail.side_effect = Exception("SMTP Error")
        data: dict[str, Any] = {"email": "test@example.com"}
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 500)


class VerifyEmailAPIViewTest(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/accounts/verification/verify-email/"
        self.email = "test@example.com"
        self.code = "ABC123"
        save_email_code(self.email, self.code)

    def test_verify_email_success(self) -> None:
        data: dict[str, Any] = {"email": self.email, "code": self.code}
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("email_token", response.json())

    def test_verify_email_wrong_code(self) -> None:
        data: dict[str, Any] = {"email": self.email, "code": "WRONG1"}
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_verify_email_expired_code(self) -> None:
        data: dict[str, Any] = {"email": "notexist@example.com", "code": "ABC123"}
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_verify_email_missing_fields(self) -> None:
        data: dict[str, Any] = {"email": self.email}
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
