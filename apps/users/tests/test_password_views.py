from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.users.models import User
from apps.users.utils.redis_utils import save_email_token


class ChangePasswordAPITest(TestCase):
    """비밀번호 변경 API 테스트."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@example.com",
            password="OldPass123!",
            name="테스트",
            nickname="테스트유저",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            is_active=True,
        )
        self.api_client = APIClient()

    def test_change_password_success(self) -> None:
        token = AccessToken.for_user(self.user)
        self.api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.api_client.post(
            "/api/v1/accounts/change-password/",
            data={
                "old_password": "OldPass123!",
                "new_password": "NewPass456@",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detail"], "비밀번호 변경 성공.")

        # 새 비밀번호로 로그인 가능한지 확인
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass456@"))

    def test_change_password_wrong_old_password(self) -> None:
        token = AccessToken.for_user(self.user)
        self.api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.api_client.post(
            "/api/v1/accounts/change-password/",
            data={
                "old_password": "WrongPass123!",
                "new_password": "NewPass456@",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("old_password", response.json()["error_detail"])

    def test_change_password_invalid_new_password(self) -> None:
        token = AccessToken.for_user(self.user)
        self.api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.api_client.post(
            "/api/v1/accounts/change-password/",
            data={
                "old_password": "OldPass123!",
                "new_password": "weak",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("new_password", response.json()["error_detail"])

    def test_change_password_unauthenticated(self) -> None:
        response = self.api_client.post(
            "/api/v1/accounts/change-password/",
            data={
                "old_password": "OldPass123!",
                "new_password": "NewPass456@",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)


class FindPasswordAPITest(TestCase):
    """비밀번호 분실 재설정 API 테스트."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@example.com",
            password="OldPass123!",
            name="테스트",
            nickname="테스트유저",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            is_active=True,
        )

    def test_find_password_success(self) -> None:
        # email_token 저장
        email_token = "test_email_token_12345"
        save_email_token(email_token, self.user.email)

        response = self.client.post(
            "/api/v1/accounts/find-password/",
            data={
                "email_token": email_token,
                "new_password": "NewPass456@",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detail"], "비밀번호 변경 성공.")

        # 새 비밀번호로 로그인 가능한지 확인
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass456@"))

    def test_find_password_invalid_token(self) -> None:
        response = self.client.post(
            "/api/v1/accounts/find-password/",
            data={
                "email_token": "invalid_token",
                "new_password": "NewPass456@",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email_token", response.json()["error_detail"])

    def test_find_password_invalid_new_password(self) -> None:
        email_token = "test_email_token_12345"
        save_email_token(email_token, self.user.email)

        response = self.client.post(
            "/api/v1/accounts/find-password/",
            data={
                "email_token": email_token,
                "new_password": "weak",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("new_password", response.json()["error_detail"])


class TokenRefreshAPITest(TestCase):
    """JWT 토큰 재발급 API 테스트."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            name="테스트",
            nickname="테스트유저",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            is_active=True,
        )

    def test_token_refresh_success(self) -> None:
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(
            "/api/v1/accounts/me/refresh/",
            data={"refresh_token": str(refresh)},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

    def test_token_refresh_invalid_token(self) -> None:
        response = self.client.post(
            "/api/v1/accounts/me/refresh/",
            data={"refresh_token": "invalid_token"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error_detail"]["detail"], "로그인 세션이 만료되었습니다.")

    def test_token_refresh_missing_token(self) -> None:
        response = self.client.post(
            "/api/v1/accounts/me/refresh/",
            data={},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("refresh_token", response.json()["error_detail"])
