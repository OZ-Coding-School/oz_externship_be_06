from typing import Any

from django.test import TestCase

from apps.users.models import User
from apps.users.utils.redis_utils import save_email_token, save_sms_token


class SignUpAPIViewTest(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/accounts/signup/"
        self.email = "test@example.com"
        self.phone_number = "01012345678"
        self.email_token = "test_email_token_12345"
        self.sms_token = "test_sms_token_12345"
        save_email_token(self.email_token, self.email)
        save_sms_token(self.sms_token, self.phone_number)

    def test_signup_success(self) -> None:
        data = {
            "email_token": self.email_token,
            "sms_token": self.sms_token,
            "password": "TestPassword123!",
            "password_confirm": "TestPassword123!",
            "nickname": "testuser",
            "name": "테스트",
            "birthday": "1990-01-01",
            "gender": "M",
        }
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email=self.email).exists())
        # 인증 완료 후 회원가입했으므로 is_active=True 확인
        user = User.objects.get(email=self.email)
        self.assertTrue(user.is_active)

    def test_signup_missing_required_field(self) -> None:
        data = {
            "email_token": self.email_token,
            "password": "TestPassword123!",
        }
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_signup_password_mismatch(self) -> None:
        data = {
            "email_token": self.email_token,
            "sms_token": self.sms_token,
            "password": "TestPassword123!",
            "password_confirm": "DifferentPassword123!",
            "nickname": "testuser",
            "name": "테스트",
            "birthday": "1990-01-01",
            "gender": "M",
        }
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_signup_invalid_email_token(self) -> None:
        data = {
            "email_token": "invalid_token",
            "sms_token": self.sms_token,
            "password": "TestPassword123!",
            "password_confirm": "TestPassword123!",
            "nickname": "testuser",
            "name": "테스트",
            "birthday": "1990-01-01",
            "gender": "M",
        }
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_signup_duplicate_nickname(self) -> None:
        User.objects.create_user(
            email="existing@example.com",
            password="TestPassword123!",
            nickname="existing",
            name="기존유저",
            birthday="1990-01-01",
            gender="MALE",
            phone_number="01099999999",
        )
        data = {
            "email_token": self.email_token,
            "sms_token": self.sms_token,
            "password": "TestPassword123!",
            "password_confirm": "TestPassword123!",
            "nickname": "existing",
            "name": "테스트",
            "birthday": "1990-01-01",
            "gender": "M",
        }
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)


class SignupNicknameCheckAPIViewTest(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/accounts/check-nickname/"

    def test_nickname_available(self) -> None:
        data = {"nickname": "newuser"}
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_nickname_already_exists(self) -> None:
        User.objects.create_user(
            email="existing@example.com",
            password="TestPassword123!",
            nickname="existing",
            name="기존유저",
            birthday="1990-01-01",
            gender="MALE",
            phone_number="01012345678",
        )
        data = {"nickname": "existing"}
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 409)

    def test_nickname_missing(self) -> None:
        data: dict[str, Any] = {}
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_nickname_too_long(self) -> None:
        data = {"nickname": "a" * 11}
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
