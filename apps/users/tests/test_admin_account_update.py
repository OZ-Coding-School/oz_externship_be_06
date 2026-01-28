from datetime import date
from typing import Any

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import User


class AdminAccountUpdateAPITest(TestCase):
    """어드민 회원 정보 수정 API 테스트."""

    def setUp(self) -> None:
        self.client = APIClient()

        # 관리자 유저
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            name="관리자",
            nickname="관리자",
            phone_number="01011111111",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
            role=User.Role.ADMIN,
        )

        # 조교 유저
        self.ta_user = User.objects.create_user(
            email="ta@example.com",
            password="password123",
            name="조교",
            nickname="조교",
            phone_number="01022222222",
            gender=User.Gender.FEMALE,
            birthday=date(1995, 5, 5),
            role=User.Role.TA,
        )

        # 일반 유저 (수정 대상)
        self.target_user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            name="홍길동",
            nickname="길동이",
            phone_number="01033333333",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.USER,
        )

        # 일반 유저 (권한 없음)
        self.normal_user = User.objects.create_user(
            email="normal@example.com",
            password="password123",
            name="일반유저",
            nickname="일반유저",
            phone_number="01044444444",
            gender=User.Gender.FEMALE,
            birthday=date(2000, 2, 2),
            role=User.Role.USER,
        )

    def _get_url(self, account_id: int) -> str:
        return f"/api/v1/admin/accounts/{account_id}/"

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_admin_can_update_user_name(self) -> None:
        """관리자가 회원 이름을 수정할 수 있다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"name": "김철수"},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "김철수")

        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.name, "김철수")

    def test_ta_can_update_user_info(self) -> None:
        """조교가 회원 정보를 수정할 수 있다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"nickname": "새닉네임"},
            content_type="application/json",
            **self._auth_headers(self.ta_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["nickname"], "새닉네임")

    def test_can_update_multiple_fields(self) -> None:
        """여러 필드를 동시에 수정할 수 있다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={
                "name": "이영희",
                "nickname": "영희",
                "gender": "FEMALE",
                "birthday": "1999-12-31",
                "phone_number": "01099999999",
            },
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "이영희")
        self.assertEqual(data["nickname"], "영희")
        self.assertEqual(data["birthday"], "1999-12-31")
        self.assertEqual(data["phone_number"], "01099999999")

    def test_can_update_is_active(self) -> None:
        """회원 상태(is_active)를 수정할 수 있다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"is_active": False},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["is_active"], False)

        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.is_active, False)

    def test_returns_401_when_unauthenticated(self) -> None:
        """인증되지 않은 사용자는 401을 받는다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"name": "새이름"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_403_for_normal_user(self) -> None:
        """일반 유저는 403을 받는다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"name": "새이름"},
            content_type="application/json",
            **self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        data = response.json()
        self.assertEqual(data["detail"], "권한이 없습니다.")

    def test_returns_404_when_user_not_found(self) -> None:
        """존재하지 않는 회원 수정 시 404를 받는다."""
        response = self.client.patch(
            self._get_url(99999),
            data={"name": "새이름"},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertEqual(data["error_detail"], "사용자 정보를 찾을 수 없습니다.")

    def test_returns_400_for_invalid_phone_number(self) -> None:
        """잘못된 전화번호 형식은 400을 받는다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"phone_number": "010-1234-5678"},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_for_short_phone_number(self) -> None:
        """11자리가 아닌 전화번호는 400을 받는다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"phone_number": "0101234"},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_for_empty_data(self) -> None:
        """수정할 데이터가 없으면 400을 받는다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data["error_detail"], "수정할 항목이 없습니다.")

    def test_returns_409_for_duplicate_phone_number(self) -> None:
        """중복된 전화번호는 409를 받는다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"phone_number": self.admin_user.phone_number},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        data = response.json()
        self.assertIn("휴대폰 번호 중복", data["error_detail"])

    def test_returns_409_for_duplicate_nickname(self) -> None:
        """중복된 닉네임은 409를 받는다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"nickname": self.admin_user.nickname},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        data = response.json()
        self.assertIn("닉네임 중복", data["error_detail"])

    def test_same_phone_number_allowed_for_same_user(self) -> None:
        """본인의 기존 전화번호는 그대로 사용 가능하다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"phone_number": self.target_user.phone_number, "name": "새이름"},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
