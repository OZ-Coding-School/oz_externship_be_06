from datetime import date
from typing import Any

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import User


class AdminAccountDeleteAPITest(TestCase):
    """어드민 회원 정보 삭제 API 테스트."""

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

        # 러닝코치 유저
        self.lc_user = User.objects.create_user(
            email="lc@example.com",
            password="password123",
            name="러닝코치",
            nickname="러닝코치",
            phone_number="01033333333",
            gender=User.Gender.MALE,
            birthday=date(1992, 3, 3),
            role=User.Role.LC,
        )

        # 운영매니저 유저
        self.om_user = User.objects.create_user(
            email="om@example.com",
            password="password123",
            name="운영매니저",
            nickname="운영매니저",
            phone_number="01044444444",
            gender=User.Gender.FEMALE,
            birthday=date(1993, 4, 4),
            role=User.Role.OM,
        )

        # 일반 유저 (삭제 대상)
        self.target_user = User.objects.create_user(
            email="target@example.com",
            password="password123",
            name="삭제대상",
            nickname="삭제대상",
            phone_number="01055555555",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.USER,
        )

        # 일반 유저
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            name="일반유저",
            nickname="일반유저",
            phone_number="01066666666",
            gender=User.Gender.MALE,
            birthday=date(2000, 2, 2),
            role=User.Role.USER,
        )

    def _get_url(self, account_id: int) -> str:
        return f"/api/v1/admin/accounts/{account_id}/"

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_admin_can_delete_user(self) -> None:
        """관리자가 회원을 삭제할 수 있다."""
        target_id = self.target_user.id

        response = self.client.delete(
            self._get_url(target_id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["detail"], f"유저 데이터가 삭제되었습니다. - pk: {target_id}")

        # 실제로 삭제되었는지 확인
        self.assertFalse(User.objects.filter(id=target_id).exists())

    def test_ta_cannot_delete_user(self) -> None:
        """조교는 회원을 삭제할 수 없다."""
        response = self.client.delete(
            self._get_url(self.target_user.id),
            **self._auth_headers(self.ta_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        data = response.json()
        self.assertEqual(data["detail"], "권한이 없습니다.")

    def test_lc_cannot_delete_user(self) -> None:
        """러닝코치는 회원을 삭제할 수 없다."""
        response = self.client.delete(
            self._get_url(self.target_user.id),
            **self._auth_headers(self.lc_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        data = response.json()
        self.assertEqual(data["detail"], "권한이 없습니다.")

    def test_om_cannot_delete_user(self) -> None:
        """운영매니저는 회원을 삭제할 수 없다."""
        response = self.client.delete(
            self._get_url(self.target_user.id),
            **self._auth_headers(self.om_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        data = response.json()
        self.assertEqual(data["detail"], "권한이 없습니다.")

    def test_normal_user_cannot_delete_user(self) -> None:
        """일반 유저는 회원을 삭제할 수 없다."""
        response = self.client.delete(
            self._get_url(self.target_user.id),
            **self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        data = response.json()
        self.assertEqual(data["detail"], "권한이 없습니다.")

    def test_returns_401_when_unauthenticated(self) -> None:
        """인증되지 않은 사용자는 401을 받는다."""
        response = self.client.delete(self._get_url(self.target_user.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_404_when_user_not_found(self) -> None:
        """존재하지 않는 회원 삭제 시 404를 받는다."""
        response = self.client.delete(
            self._get_url(99999),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertEqual(data["error_detail"], "사용자 정보를 찾을 수 없습니다.")

    def test_admin_can_delete_staff_user(self) -> None:
        """관리자가 스태프(조교) 유저도 삭제할 수 있다."""
        ta_id = self.ta_user.id

        response = self.client.delete(
            self._get_url(ta_id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.filter(id=ta_id).exists())
