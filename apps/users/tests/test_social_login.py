from datetime import date
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from apps.users.models import Withdrawal
from apps.users.models.social_user import SocialUser
from apps.users.utils.social_login import (
    KakaoOAuthService,
    NaverOAuthService,
    parse_kakao_birthday,
    parse_naver_birthday,
)

User = get_user_model()


class ParseKakaoBirthdayTests(TestCase):
    def test_valid_birthday(self) -> None:
        result = parse_kakao_birthday({"birthday": "0315"})
        self.assertEqual(result, date(2000, 3, 15))

    def test_empty_birthday(self) -> None:
        result = parse_kakao_birthday({})
        self.assertIsNone(result)

    def test_none_birthday(self) -> None:
        result = parse_kakao_birthday({"birthday": None})
        self.assertIsNone(result)

    def test_invalid_length(self) -> None:
        result = parse_kakao_birthday({"birthday": "315"})
        self.assertIsNone(result)

    def test_invalid_format(self) -> None:
        result = parse_kakao_birthday({"birthday": "abcd"})
        self.assertIsNone(result)

    def test_invalid_date(self) -> None:
        result = parse_kakao_birthday({"birthday": "1332"})
        self.assertIsNone(result)


class ParseNaverBirthdayTests(TestCase):
    def test_valid_birthday(self) -> None:
        result = parse_naver_birthday({"birthyear": "1995", "birthday": "03-15"})
        self.assertEqual(result, date(1995, 3, 15))

    def test_missing_birthyear(self) -> None:
        result = parse_naver_birthday({"birthday": "03-15"})
        self.assertIsNone(result)

    def test_missing_birthday(self) -> None:
        result = parse_naver_birthday({"birthyear": "1995"})
        self.assertIsNone(result)

    def test_empty_profile(self) -> None:
        result = parse_naver_birthday({})
        self.assertIsNone(result)

    def test_invalid_year(self) -> None:
        result = parse_naver_birthday({"birthyear": "abcd", "birthday": "03-15"})
        self.assertIsNone(result)

    def test_invalid_birthday_format(self) -> None:
        result = parse_naver_birthday({"birthyear": "1995", "birthday": "abcd"})
        self.assertIsNone(result)


class KakaoOAuthServiceTests(TestCase):
    def setUp(self) -> None:
        self.service = KakaoOAuthService()

    @patch("apps.users.utils.social_login.requests.post")
    def test_get_access_token_success(self, mock_post: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = mock_response

        token = self.service.get_access_token("test_code")

        self.assertEqual(token, "test_token")
        mock_response.raise_for_status.assert_called_once()

    @patch("apps.users.utils.social_login.requests.get")
    def test_get_user_info_success(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": 12345,
            "kakao_account": {"email": "test@kakao.com"},
        }
        mock_get.return_value = mock_response

        user_info = self.service.get_user_info("test_token")

        self.assertEqual(user_info["id"], 12345)
        mock_response.raise_for_status.assert_called_once()

    def test_get_or_create_user_new_user(self) -> None:
        profile = {
            "id": 12345,
            "kakao_account": {
                "email": "newuser@kakao.com",
                "profile": {"nickname": "카카오유저"},
                "gender": "male",
                "birthday": "0315",
            },
        }

        user = self.service.get_or_create_user(profile)

        self.assertEqual(user.email, "newuser@kakao.com")
        self.assertEqual(user.nickname, "카카오유저")
        self.assertEqual(user.gender, User.Gender.MALE)
        self.assertTrue(
            SocialUser.objects.filter(
                user=user,
                provider=SocialUser.Provider.KAKAO,
                provider_id="12345",
            ).exists()
        )

    def test_get_or_create_user_existing_social_user(self) -> None:
        existing_user = User.objects.create_user(
            email="existing@kakao.com",
            nickname="기존유저",
            name="기존유저",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
        )
        SocialUser.objects.create(
            user=existing_user,
            provider=SocialUser.Provider.KAKAO,
            provider_id="12345",
        )

        profile = {
            "id": 12345,
            "kakao_account": {
                "email": "different@kakao.com",
                "profile": {"nickname": "새닉네임"},
            },
        }

        user = self.service.get_or_create_user(profile)

        self.assertEqual(user.id, existing_user.id)
        self.assertEqual(user.email, "existing@kakao.com")

    def test_get_or_create_user_existing_email_user(self) -> None:
        existing_user = User.objects.create_user(
            email="samemail@kakao.com",
            nickname="기존유저",
            name="기존유저",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
        )

        profile = {
            "id": 99999,
            "kakao_account": {
                "email": "samemail@kakao.com",
                "profile": {"nickname": "카카오닉네임"},
            },
        }

        user = self.service.get_or_create_user(profile)

        self.assertEqual(user.id, existing_user.id)
        self.assertTrue(
            SocialUser.objects.filter(
                user=user,
                provider=SocialUser.Provider.KAKAO,
                provider_id="99999",
            ).exists()
        )

    def test_get_or_create_user_no_email(self) -> None:
        profile = {
            "id": 12345,
            "kakao_account": {"profile": {"nickname": "노이메일"}},
        }

        with self.assertRaises(ValidationError) as context:
            self.service.get_or_create_user(profile)

        detail = context.exception.detail
        assert isinstance(detail, dict)
        self.assertEqual(detail["code"], "email_required")

    def test_get_or_create_user_female_gender(self) -> None:
        profile = {
            "id": 11111,
            "kakao_account": {
                "email": "female@kakao.com",
                "profile": {"nickname": "여성유저"},
                "gender": "female",
            },
        }

        user = self.service.get_or_create_user(profile)

        self.assertEqual(user.gender, User.Gender.FEMALE)

    def test_get_or_create_user_no_nickname(self) -> None:
        profile = {
            "id": 22222,
            "kakao_account": {
                "email": "nonickname@kakao.com",
                "profile": {},
            },
        }

        user = self.service.get_or_create_user(profile)

        self.assertEqual(user.nickname, "kakao_2222")
        self.assertEqual(user.name, "카카오유저")


class NaverOAuthServiceTests(TestCase):
    def setUp(self) -> None:
        self.service = NaverOAuthService()

    @patch("apps.users.utils.social_login.requests.post")
    def test_get_access_token_success(self, mock_post: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "naver_token"}
        mock_post.return_value = mock_response

        token = self.service.get_access_token("test_code", "test_state")

        self.assertEqual(token, "naver_token")
        mock_response.raise_for_status.assert_called_once()

    @patch("apps.users.utils.social_login.requests.get")
    def test_get_user_info_success(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": {"id": "naver123", "email": "test@naver.com"}}
        mock_get.return_value = mock_response

        user_info = self.service.get_user_info("naver_token")

        self.assertEqual(user_info["id"], "naver123")
        self.assertEqual(user_info["email"], "test@naver.com")

    @patch("apps.users.utils.social_login.requests.get")
    def test_get_user_info_empty_response(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": None}
        mock_get.return_value = mock_response

        with self.assertRaises(ValidationError) as context:
            self.service.get_user_info("naver_token")

        detail = context.exception.detail
        assert isinstance(detail, dict)
        self.assertEqual(detail["code"], "naver_api_error")

    def test_get_or_create_user_new_user(self) -> None:
        profile = {
            "id": "naver123",
            "email": "newuser@naver.com",
            "nickname": "네이버유저",
            "name": "홍길동",
            "gender": "M",
            "birthyear": "1995",
            "birthday": "03-15",
            "mobile": "010-1234-5678",
        }

        user = self.service.get_or_create_user(profile)

        self.assertEqual(user.email, "newuser@naver.com")
        self.assertEqual(user.nickname, "네이버유저")
        self.assertEqual(user.name, "홍길동")
        self.assertEqual(user.gender, User.Gender.MALE)
        self.assertEqual(user.birthday, date(1995, 3, 15))
        self.assertEqual(user.phone_number, "01012345678")
        self.assertTrue(
            SocialUser.objects.filter(
                user=user,
                provider=SocialUser.Provider.NAVER,
                provider_id="naver123",
            ).exists()
        )

    def test_get_or_create_user_existing_social_user(self) -> None:
        existing_user = User.objects.create_user(
            email="existing@naver.com",
            nickname="기존유저",
            name="기존유저",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
        )
        SocialUser.objects.create(
            user=existing_user,
            provider=SocialUser.Provider.NAVER,
            provider_id="naver123",
        )

        profile = {
            "id": "naver123",
            "email": "different@naver.com",
            "nickname": "새닉네임",
        }

        user = self.service.get_or_create_user(profile)

        self.assertEqual(user.id, existing_user.id)

    def test_get_or_create_user_existing_email_user(self) -> None:
        existing_user = User.objects.create_user(
            email="samemail@naver.com",
            nickname="기존유저",
            name="기존유저",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
        )

        profile = {
            "id": "naver999",
            "email": "samemail@naver.com",
            "nickname": "네이버닉네임",
        }

        user = self.service.get_or_create_user(profile)

        self.assertEqual(user.id, existing_user.id)
        self.assertTrue(
            SocialUser.objects.filter(
                user=user,
                provider=SocialUser.Provider.NAVER,
                provider_id="naver999",
            ).exists()
        )

    def test_get_or_create_user_no_email(self) -> None:
        profile = {"id": "naver123", "nickname": "노이메일"}

        with self.assertRaises(ValidationError) as context:
            self.service.get_or_create_user(profile)

        detail = context.exception.detail
        assert isinstance(detail, dict)
        self.assertEqual(detail["code"], "email_required")

    def test_get_or_create_user_female_gender(self) -> None:
        profile = {
            "id": "naver_female",
            "email": "female@naver.com",
            "nickname": "여성유저",
            "gender": "F",
        }

        user = self.service.get_or_create_user(profile)

        self.assertEqual(user.gender, User.Gender.FEMALE)

    def test_get_or_create_user_no_nickname(self) -> None:
        profile = {
            "id": "naver_no_nick",
            "email": "nonickname@naver.com",
        }

        user = self.service.get_or_create_user(profile)

        self.assertEqual(user.nickname, "naver_nave")
        self.assertEqual(user.name, "네이버유저")


@override_settings(
    KAKAO_CLIENT_ID="test_kakao_client_id",
    KAKAO_REDIRECT_URI="http://127.0.0.1:8000/api/v1/accounts/login/kakao/callback/",
    NAVER_CLIENT_ID="test_naver_client_id",
    NAVER_CLIENT_SECRET="test_naver_secret",
    NAVER_REDIRECT_URI="http://127.0.0.1:8000/api/v1/accounts/login/naver/callback/",
    FRONTEND_SOCIAL_REDIRECT_URL="http://localhost:3000/auth/callback",
)
class KakaoLoginViewTests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()

    def test_kakao_login_start_redirect(self) -> None:
        res = self.client.get("/api/v1/accounts/login/kakao/")

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.assertIn("kauth.kakao.com", res["Location"])
        self.assertIn("client_id=test_kakao_client_id", res["Location"])

    @patch.object(KakaoOAuthService, "get_access_token")
    @patch.object(KakaoOAuthService, "get_user_info")
    def test_kakao_callback_success(self, mock_get_user_info: MagicMock, mock_get_access_token: MagicMock) -> None:
        mock_get_access_token.return_value = "test_access_token"
        mock_get_user_info.return_value = {
            "id": 12345,
            "kakao_account": {
                "email": "callback@kakao.com",
                "profile": {"nickname": "콜백유저"},
            },
        }

        session = self.client.session
        session["oauth_state_kakao"] = "valid_state"
        session.save()

        res = self.client.get(
            "/api/v1/accounts/login/kakao/callback/",
            {"code": "test_code", "state": "valid_state"},
        )

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.assertIn("localhost:3000", res["Location"])
        self.assertIn("is_success=true", res["Location"])

    def test_kakao_callback_missing_code(self) -> None:
        res = self.client.get(
            "/api/v1/accounts/login/kakao/callback/",
            {"state": "some_state"},
        )

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.assertIn("is_success=false", res["Location"])

    def test_kakao_callback_invalid_state(self) -> None:
        session = self.client.session
        session["oauth_state_kakao"] = "valid_state"
        session.save()

        res = self.client.get(
            "/api/v1/accounts/login/kakao/callback/",
            {"code": "test_code", "state": "invalid_state"},
        )

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.assertIn("is_success=false", res["Location"])

    @patch.object(KakaoOAuthService, "get_access_token")
    @patch.object(KakaoOAuthService, "get_user_info")
    def test_kakao_callback_inactive_user(
        self, mock_get_user_info: MagicMock, mock_get_access_token: MagicMock
    ) -> None:
        inactive_user = User.objects.create_user(
            email="inactive@kakao.com",
            nickname="비활성",
            name="비활성유저",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
            is_active=False,
        )
        SocialUser.objects.create(
            user=inactive_user,
            provider=SocialUser.Provider.KAKAO,
            provider_id="inactive123",
        )

        mock_get_access_token.return_value = "test_access_token"
        mock_get_user_info.return_value = {
            "id": "inactive123",
            "kakao_account": {
                "email": "inactive@kakao.com",
                "profile": {"nickname": "비활성"},
            },
        }

        session = self.client.session
        session["oauth_state_kakao"] = "valid_state"
        session.save()

        res = self.client.get(
            "/api/v1/accounts/login/kakao/callback/",
            {"code": "test_code", "state": "valid_state"},
        )

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.assertIn("is_success=false", res["Location"])

    @patch.object(KakaoOAuthService, "get_access_token")
    @patch.object(KakaoOAuthService, "get_user_info")
    def test_kakao_callback_withdrawn_user(
        self, mock_get_user_info: MagicMock, mock_get_access_token: MagicMock
    ) -> None:
        withdrawn_user = User.objects.create_user(
            email="withdrawn@kakao.com",
            nickname="탈퇴유저",
            name="탈퇴유저",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
        )
        Withdrawal.objects.create(user=withdrawn_user, reason="SERVICE_DISSATISFACTION")
        SocialUser.objects.create(
            user=withdrawn_user,
            provider=SocialUser.Provider.KAKAO,
            provider_id="withdrawn123",
        )

        mock_get_access_token.return_value = "test_access_token"
        mock_get_user_info.return_value = {
            "id": "withdrawn123",
            "kakao_account": {
                "email": "withdrawn@kakao.com",
                "profile": {"nickname": "탈퇴유저"},
            },
        }

        session = self.client.session
        session["oauth_state_kakao"] = "valid_state"
        session.save()

        res = self.client.get(
            "/api/v1/accounts/login/kakao/callback/",
            {"code": "test_code", "state": "valid_state"},
        )

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.assertIn("is_success=false", res["Location"])


@override_settings(
    KAKAO_CLIENT_ID="test_kakao_client_id",
    KAKAO_REDIRECT_URI="http://127.0.0.1:8000/api/v1/accounts/login/kakao/callback/",
    NAVER_CLIENT_ID="test_naver_client_id",
    NAVER_CLIENT_SECRET="test_naver_secret",
    NAVER_REDIRECT_URI="http://127.0.0.1:8000/api/v1/accounts/login/naver/callback/",
    FRONTEND_SOCIAL_REDIRECT_URL="http://localhost:3000/auth/callback",
)
class NaverLoginViewTests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()

    def test_naver_login_start_redirect(self) -> None:
        res = self.client.get("/api/v1/accounts/login/naver/")

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.assertIn("nid.naver.com", res["Location"])
        self.assertIn("client_id=test_naver_client_id", res["Location"])

    @patch.object(NaverOAuthService, "get_access_token")
    @patch.object(NaverOAuthService, "get_user_info")
    def test_naver_callback_success(self, mock_get_user_info: MagicMock, mock_get_access_token: MagicMock) -> None:
        mock_get_access_token.return_value = "test_access_token"
        mock_get_user_info.return_value = {
            "id": "naver12345",
            "email": "callback@naver.com",
            "nickname": "콜백유저",
            "name": "네이버유저",
        }

        session = self.client.session
        session["oauth_state_naver"] = "valid_state"
        session.save()

        res = self.client.get(
            "/api/v1/accounts/login/naver/callback/",
            {"code": "test_code", "state": "valid_state"},
        )

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.assertIn("localhost:3000", res["Location"])
        self.assertIn("is_success=true", res["Location"])

    def test_naver_callback_missing_code(self) -> None:
        res = self.client.get(
            "/api/v1/accounts/login/naver/callback/",
            {"state": "some_state"},
        )

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.assertIn("is_success=false", res["Location"])

    def test_naver_callback_invalid_state(self) -> None:
        session = self.client.session
        session["oauth_state_naver"] = "valid_state"
        session.save()

        res = self.client.get(
            "/api/v1/accounts/login/naver/callback/",
            {"code": "test_code", "state": "invalid_state"},
        )

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.assertIn("is_success=false", res["Location"])

    @patch.object(NaverOAuthService, "get_access_token")
    @patch.object(NaverOAuthService, "get_user_info")
    def test_naver_callback_inactive_user(
        self, mock_get_user_info: MagicMock, mock_get_access_token: MagicMock
    ) -> None:
        inactive_user = User.objects.create_user(
            email="inactive@naver.com",
            nickname="비활성",
            name="비활성유저",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
            is_active=False,
        )
        SocialUser.objects.create(
            user=inactive_user,
            provider=SocialUser.Provider.NAVER,
            provider_id="inactive_naver",
        )

        mock_get_access_token.return_value = "test_access_token"
        mock_get_user_info.return_value = {
            "id": "inactive_naver",
            "email": "inactive@naver.com",
            "nickname": "비활성",
        }

        session = self.client.session
        session["oauth_state_naver"] = "valid_state"
        session.save()

        res = self.client.get(
            "/api/v1/accounts/login/naver/callback/",
            {"code": "test_code", "state": "valid_state"},
        )

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.assertIn("is_success=false", res["Location"])

    @patch.object(NaverOAuthService, "get_access_token")
    @patch.object(NaverOAuthService, "get_user_info")
    def test_naver_callback_withdrawn_user(
        self, mock_get_user_info: MagicMock, mock_get_access_token: MagicMock
    ) -> None:
        withdrawn_user = User.objects.create_user(
            email="withdrawn@naver.com",
            nickname="탈퇴유저",
            name="탈퇴유저",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
        )
        Withdrawal.objects.create(user=withdrawn_user, reason="SERVICE_DISSATISFACTION")
        SocialUser.objects.create(
            user=withdrawn_user,
            provider=SocialUser.Provider.NAVER,
            provider_id="withdrawn_naver",
        )

        mock_get_access_token.return_value = "test_access_token"
        mock_get_user_info.return_value = {
            "id": "withdrawn_naver",
            "email": "withdrawn@naver.com",
            "nickname": "탈퇴유저",
        }

        session = self.client.session
        session["oauth_state_naver"] = "valid_state"
        session.save()

        res = self.client.get(
            "/api/v1/accounts/login/naver/callback/",
            {"code": "test_code", "state": "valid_state"},
        )

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
        self.assertIn("is_success=false", res["Location"])
