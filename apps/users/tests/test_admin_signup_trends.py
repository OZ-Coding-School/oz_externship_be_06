from datetime import date
from typing import Any

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import User


class AdminSignupTrendsAPITest(TestCase):
    """어드민 회원가입 추세 분석 API 테스트."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/admin/analytics/signup/trends"

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

        # 일반 유저 (권한 없음)
        self.normal_user = User.objects.create_user(
            email="normal@example.com",
            password="password123",
            name="일반유저",
            nickname="일반유저",
            phone_number="01077777777",
            gender=User.Gender.MALE,
            birthday=date(2000, 5, 5),
            role=User.Role.USER,
        )

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_admin_can_get_monthly_trends(self) -> None:
        """관리자가 월별 회원가입 추세를 조회할 수 있다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["interval"], "monthly")
        self.assertIn("from_date", data)
        self.assertIn("to_date", data)
        self.assertIn("total", data)
        self.assertIn("items", data)
        # 1~12월이므로 12개 항목
        self.assertEqual(len(data["items"]), 12)

    def test_admin_can_get_monthly_trends_with_year(self) -> None:
        """관리자가 특정 연도의 월별 회원가입 추세를 조회할 수 있다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly", "year": 2025},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["interval"], "monthly")
        self.assertEqual(data["from_date"], "2025-01-01")
        self.assertEqual(data["to_date"], "2025-12-31")
        self.assertEqual(len(data["items"]), 12)

        # 첫 번째 항목은 1월
        self.assertEqual(data["items"][0]["period"], "2025-01")
        # 마지막 항목은 12월
        self.assertEqual(data["items"][11]["period"], "2025-12")

    def test_admin_can_get_yearly_trends(self) -> None:
        """관리자가 년별 회원가입 추세를 조회할 수 있다."""
        response = self.client.get(
            self.url,
            {"interval": "yearly"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["interval"], "yearly")
        # 최소 1개 이상의 연도 데이터
        self.assertGreaterEqual(len(data["items"]), 1)

    def test_ta_can_get_trends(self) -> None:
        """조교가 회원가입 추세를 조회할 수 있다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly"},
            **self._auth_headers(self.ta_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_format(self) -> None:
        """응답 형식이 명세서와 일치한다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # 필수 필드 확인
        self.assertIn("interval", data)
        self.assertIn("from_date", data)
        self.assertIn("to_date", data)
        self.assertIn("total", data)
        self.assertIn("items", data)

        # items 항목 형식 확인
        if len(data["items"]) > 0:
            item = data["items"][0]
            self.assertIn("period", item)
            self.assertIn("count", item)

    def test_monthly_period_format(self) -> None:
        """월별 period 형식이 YYYY-MM이다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # period 형식 확인 (YYYY-MM)
        for item in data["items"]:
            self.assertRegex(item["period"], r"^\d{4}-\d{2}$")

    def test_yearly_period_format(self) -> None:
        """년별 period 형식이 YYYY이다."""
        response = self.client.get(
            self.url,
            {"interval": "yearly"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # period 형식 확인 (YYYY)
        for item in data["items"]:
            self.assertRegex(item["period"], r"^\d{4}$")

    def test_total_equals_sum_of_counts(self) -> None:
        """total이 items의 count 합계와 일치한다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        expected_total = sum(item["count"] for item in data["items"])
        self.assertEqual(data["total"], expected_total)

    def test_returns_400_without_interval(self) -> None:
        """interval 없이 요청하면 400을 받는다."""
        response = self.client.get(
            self.url,
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_with_invalid_interval(self) -> None:
        """잘못된 interval로 요청하면 400을 받는다."""
        response = self.client.get(
            self.url,
            {"interval": "weekly"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_401_when_unauthenticated(self) -> None:
        """인증되지 않은 사용자는 401을 받는다."""
        response = self.client.get(self.url, {"interval": "monthly"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_403_for_normal_user(self) -> None:
        """일반 유저는 403을 받는다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly"},
            **self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_counts_users_in_current_month(self) -> None:
        """현재 월에 가입한 유저 수가 정확하게 집계된다."""
        current_year = date.today().year
        response = self.client.get(
            self.url,
            {"interval": "monthly", "year": current_year},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # 현재 월의 count가 최소 3 이상 (admin, ta, normal)
        current_period = date.today().strftime("%Y-%m")
        current_item = next(
            (item for item in data["items"] if item["period"] == current_period), None
        )
        assert current_item is not None
        self.assertGreaterEqual(current_item["count"], 3)

    def test_monthly_items_ordered_by_month(self) -> None:
        """월별 items가 1월부터 12월 순서로 정렬된다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly", "year": 2025},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        periods = [item["period"] for item in data["items"]]
        expected = [f"2025-{m:02d}" for m in range(1, 13)]
        self.assertEqual(periods, expected)
