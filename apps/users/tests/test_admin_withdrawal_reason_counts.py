from datetime import date, datetime
from typing import Any

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import User, Withdrawal


class AdminWithdrawalReasonCountsAPITest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/admin/analytics/withdrawals/reasons/counts/"

        self.admin_user = User.objects.create_user(
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

        self.normal_user = User.objects.create_user(
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

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_unauthenticated_request_returns_401(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_general_user_request_returns_403(self) -> None:
        response = self.client.get(self.url, **self._auth_headers(self.normal_user))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("error_detail"), "권한이 없습니다.")

    def test_admin_user_request_returns_200(self) -> None:
        response = self.client.get(self.url, **self._auth_headers(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_withdrawal_total_count(self) -> None:
        w_user = User.objects.create_user(
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
        Withdrawal.objects.create(
            user=w_user,
            reason=Withdrawal.Reason.OTHER,
            reason_detail="test",
        )

        response = self.client.get(self.url, **self._auth_headers(self.admin_user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["total"], 1)

    def test_withdrawal_item_reason(self) -> None:

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
        self.w2 = Withdrawal.objects.create(
            user=w_user2,
            reason=Withdrawal.Reason.PRIVACY_CONCERN,
            reason_detail="test",
        )
        self.w3 = Withdrawal.objects.create(
            user=w_user3,
            reason=Withdrawal.Reason.SERVICE_DISSATISFACTION,
            reason_detail="test",
        )
        response = self.client.get(self.url, **self._auth_headers(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        items = response.json()["items"]
        reason_counts = {item["reason"]: item["count"] for item in items}

        self.assertEqual(reason_counts[Withdrawal.Reason.PRIVACY_CONCERN.value], 1)  # type: ignore[misc]
        self.assertEqual(reason_counts[Withdrawal.Reason.SERVICE_DISSATISFACTION.value], 1)  # type: ignore[misc]

    def test_withdrawal_reason_label(self) -> None:

        w_user = User.objects.create_user(
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
        Withdrawal.objects.create(
            user=w_user,
            reason=Withdrawal.Reason.OTHER,
            reason_detail="test",
        )

        response = self.client.get(self.url, **self._auth_headers(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = response.json()["items"]
        self.assertIn("reason_label", items[0])

    def test_withdrawal_date(self) -> None:
        today = date.today()
        self.current_year = today.year
        self.prev_year = today.year - 1

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

        self.w2 = Withdrawal.objects.create(
            user=w_user2,
            reason=Withdrawal.Reason.PRIVACY_CONCERN,
            reason_detail="test",
        )
        self.w3 = Withdrawal.objects.create(
            user=w_user3,
            reason=Withdrawal.Reason.SERVICE_DISSATISFACTION,
            reason_detail="test",
        )

        Withdrawal.objects.filter(id=self.w2.id).update(
            created_at=timezone.make_aware(datetime(self.prev_year, 12, 10, 10, 0, 0))
        )
        Withdrawal.objects.filter(id=self.w3.id).update(
            created_at=timezone.make_aware(datetime(self.current_year, 1, 10, 10, 0, 0))
        )

        response = self.client.get(self.url, **self._auth_headers(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["from_date"], f"{self.prev_year}-12-10")
        self.assertEqual(data["to_date"], f"{self.current_year}-01-10")

    def test_withdrawal_percentage_is_100_when_single_item(self) -> None:
        w_user = User.objects.create_user(
            email="wd_percentage_1@example.com",
            password="password123",
            name="탈퇴퍼센트1",
            nickname="탈퇴퍼센트1",
            phone_number="01040000001",
            gender=User.Gender.MALE,
            birthday=date(1998, 2, 2),
            role=User.Role.USER,
            is_active=False,
        )
        Withdrawal.objects.create(
            user=w_user,
            reason=Withdrawal.Reason.OTHER,
            reason_detail="test",
        )

        response = self.client.get(self.url, **self._auth_headers(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["percentage"], 100.0)
