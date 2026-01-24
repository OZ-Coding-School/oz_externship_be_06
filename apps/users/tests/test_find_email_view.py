from datetime import date

from django.test import TestCase

from apps.users.models import User
from apps.users.utils.redis_utils import save_sms_token
from apps.users.views.find_email_view import mask_email


class MaskEmailTest(TestCase):
    """이메일 마스킹 테스트."""

    def test_mask_email_normal(self) -> None:
        result = mask_email("user@example.com")
        self.assertEqual(result, "u**r@e*****e.com")

    def test_mask_email_short_local(self) -> None:
        result = mask_email("ab@example.com")
        self.assertEqual(result, "ab@e*****e.com")

    def test_mask_email_short_domain(self) -> None:
        result = mask_email("user@ab.com")
        self.assertEqual(result, "u**r@ab.com")

    def test_mask_email_long(self) -> None:
        result = mask_email("longusername@longdomain.co.kr")
        self.assertEqual(result, "l**********e@l********n.co.kr")


class FindEmailAPITest(TestCase):
    """이메일 찾기 API 테스트."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            name="홍길동",
            nickname="테스트유저",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
        )

    def test_find_email_success(self) -> None:
        # sms_token 저장 (verify-sms에서 발급된 것처럼)
        sms_token = "test_sms_token_12345"
        save_sms_token(sms_token, "01012345678")

        response = self.client.post(
            "/api/v1/accounts/find-email/",
            data={
                "name": "홍길동",
                "sms_token": sms_token,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.json())
        # 마스킹된 이메일 확인
        self.assertEqual(response.json()["email"], "t**t@e*****e.com")

    def test_find_email_invalid_token(self) -> None:
        response = self.client.post(
            "/api/v1/accounts/find-email/",
            data={
                "name": "홍길동",
                "sms_token": "invalid_token",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("sms_token", response.json()["error_detail"])

    def test_find_email_user_not_found(self) -> None:
        # sms_token 저장
        sms_token = "test_sms_token_12345"
        save_sms_token(sms_token, "01012345678")

        response = self.client.post(
            "/api/v1/accounts/find-email/",
            data={
                "name": "존재하지않는사용자",
                "sms_token": sms_token,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.json()["error_detail"])

    def test_find_email_missing_fields(self) -> None:
        response = self.client.post(
            "/api/v1/accounts/find-email/",
            data={},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        error_detail = response.json()["error_detail"]
        self.assertIn("name", error_detail)
        self.assertIn("sms_token", error_detail)

    def test_find_email_token_deleted_after_use(self) -> None:
        # sms_token 저장
        sms_token = "test_sms_token_once"
        save_sms_token(sms_token, "01012345678")

        # 첫 번째 요청 - 성공
        response1 = self.client.post(
            "/api/v1/accounts/find-email/",
            data={
                "name": "홍길동",
                "sms_token": sms_token,
            },
            content_type="application/json",
        )
        self.assertEqual(response1.status_code, 200)

        # 두 번째 요청 - 토큰 만료
        response2 = self.client.post(
            "/api/v1/accounts/find-email/",
            data={
                "name": "홍길동",
                "sms_token": sms_token,
            },
            content_type="application/json",
        )
        self.assertEqual(response2.status_code, 400)
        self.assertIn("sms_token", response2.json()["error_detail"])
