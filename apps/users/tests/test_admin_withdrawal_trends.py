from datetime import date, datetime
from typing import Any

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import User
from apps.users.models.withdrawal import Withdrawal


class AdminWithdrawalTrendsAPITest(TestCase):

    url: str
    admin_user: User
    staff_user: User
    normal_user: User
    current_year: Any
    prev_year: Any
    w1: Withdrawal
    w2: Withdrawal
    w3: Withdrawal

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = "/api/v1/admin/analytics/withdrawals/trends"

        # 관리자 유저
        cls.admin_user = User.objects.create_user(
            email="admin_wd@example.com",
            password="password123",
            name="관리자",
            nickname="관리자",
            phone_number="01011111111",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
            role=User.Role.ADMIN,
            is_active=True,
        )

        cls.staff_user = User.objects.create_user(
            email="ta_wd@example.com",
            password="password123",
            name="조교",
            nickname="조교",
            phone_number="01022222222",
            gender=User.Gender.FEMALE,
            birthday=date(1995, 5, 5),
            role=User.Role.TA,
            is_active=True,
        )

        # 일반 유저(권한 없음)
        cls.normal_user = User.objects.create_user(
            email="normal_wd@example.com",
            password="password123",
            name="일반유저",
            nickname="일반유저",
            phone_number="01077777777",
            gender=User.Gender.MALE,
            birthday=date(2000, 5, 5),
            role=User.Role.USER,
            is_active=True,
        )

        # 탈퇴 데이터(연도/월 분산)
        today = date.today()
        cls.current_year = today.year
        cls.prev_year = today.year - 1

        w_user1 = User.objects.create_user(
            email="wd_data_1@example.com",
            password="password123",
            name="탈퇴1",
            nickname="탈퇴1",
            phone_number="01030000001",
            gender=User.Gender.MALE,
            birthday=date(1998, 1, 1),
            role=User.Role.USER,
            is_active=False,
        )
        w_user2 = User.objects.create_user(
            email="wd_data_2@example.com",
            password="password123",
            name="탈퇴2",
            nickname="탈퇴2",
            phone_number="01030000002",
            gender=User.Gender.MALE,
            birthday=date(1998, 1, 2),
            role=User.Role.USER,
            is_active=False,
        )
        w_user3 = User.objects.create_user(
            email="wd_data_3@example.com",
            password="password123",
            name="탈퇴3",
            nickname="탈퇴3",
            phone_number="01030000003",
            gender=User.Gender.MALE,
            birthday=date(1998, 1, 3),
            role=User.Role.USER,
            is_active=False,
        )

        cls.w1 = Withdrawal.objects.create(
            user=w_user1,
            reason=Withdrawal.Reason.OTHER,
            reason_detail="test",
        )
        cls.w2 = Withdrawal.objects.create(
            user=w_user2,
            reason=Withdrawal.Reason.PRIVACY_CONCERN,
            reason_detail="test",
        )
        cls.w3 = Withdrawal.objects.create(
            user=w_user3,
            reason=Withdrawal.Reason.SERVICE_DISSATISFACTION,
            reason_detail="test",
        )

        Withdrawal.objects.filter(id=cls.w1.id).update(
            created_at=timezone.make_aware(datetime(cls.prev_year, 11, 10, 10, 0, 0))
        )
        Withdrawal.objects.filter(id=cls.w2.id).update(
            created_at=timezone.make_aware(datetime(cls.prev_year, 12, 10, 10, 0, 0))
        )
        Withdrawal.objects.filter(id=cls.w3.id).update(
            created_at=timezone.make_aware(datetime(cls.current_year, 1, 10, 10, 0, 0))
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_admin_can_get_yearly_trends(self) -> None:
        response = self.client.get(
            self.url,
            {"interval": "yearly"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["interval"], "yearly")
        self.assertIn("from_date", data)
        self.assertIn("to_date", data)
        self.assertIn("total", data)
        self.assertIn("items", data)

        # prev_year, current_year 항목이 포함되는지
        periods = [item["period"] for item in data["items"]]
        self.assertIn(str(self.prev_year), periods)
        self.assertIn(str(self.current_year), periods)

        # total == sum(count)
        expected_total = sum(item["count"] for item in data["items"])
        self.assertEqual(data["total"], expected_total)

    def test_admin_can_get_monthly_trends(self) -> None:
        response = self.client.get(
            self.url,
            {"interval": "monthly"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["interval"], "monthly")
        self.assertEqual(len(data["items"]), 12)  # 1~12월

        for item in data["items"]:
            self.assertRegex(item["period"], r"^\d{4}-\d{2}$")

        jan_period = f"{self.current_year}-01"
        jan_item = next((item for item in data["items"] if item["period"] == jan_period), None)
        assert jan_item is not None
        self.assertGreaterEqual(jan_item["count"], 1)

        expected_total = sum(item["count"] for item in data["items"])
        self.assertEqual(data["total"], expected_total)

    def test_staff_can_get_trends(self) -> None:
        response = self.client.get(
            self.url,
            {"interval": "yearly"},
            **self._auth_headers(self.staff_user),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_400_without_interval(self) -> None:
        response = self.client.get(self.url, **self._auth_headers(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.json())

    def test_returns_400_with_invalid_interval(self) -> None:
        response = self.client.get(
            self.url,
            {"interval": "weekly"},
            **self._auth_headers(self.admin_user),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get("error_detail"), "잘못된 요청입니다.")

    def test_returns_401_when_unauthenticated(self) -> None:
        response = self.client.get(self.url, {"interval": "yearly"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.json().get("error_detail"),
            "자격 인증 데이터가 제공되지 않았습니다.",
        )

    def test_returns_403_for_normal_user(self) -> None:
        """일반 유저는 403을 받는다. (error_detail 포맷 확인)"""
        response = self.client.get(
            self.url,
            {"interval": "yearly"},
            **self._auth_headers(self.normal_user),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("error_detail"), "권한이 없습니다.")
