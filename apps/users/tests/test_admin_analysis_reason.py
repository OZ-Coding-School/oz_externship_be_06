from __future__ import annotations

from datetime import date

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.users.models import User
from apps.users.models.withdrawal import Withdrawal


class WithdrawalReasonMonthlyStatsAPITest(TestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            name="관리자",
            nickname="admin",
            phone_number="01000000000",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
            role=User.Role.ADMIN,
            is_active=True,
            is_staff=True,
        )
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            name="사용자",
            nickname="user",
            phone_number="01000000001",
            gender=User.Gender.MALE,
            birthday=date(1995, 1, 1),
            role=User.Role.USER,
            is_active=True,
        )
        self.url = "/api/v1/admin/analytics/withdrawal-reasons/monthly-stats"

    def test_returns_200_for_admin(self) -> None:
        withdrawal = Withdrawal.objects.create(
            user=self.normal_user,
            reason=Withdrawal.Reason.GRADUATION,
            reason_detail="done",
        )
        Withdrawal.objects.filter(id=withdrawal.id).update(created_at=timezone.now())

        self.client.force_authenticate(user=self.admin)
        res = self.client.get(self.url, {"reason": Withdrawal.Reason.GRADUATION})

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["reason"], Withdrawal.Reason.GRADUATION)
        self.assertEqual(data["total"], 1)
        self.assertGreaterEqual(len(data["items"]), 1)

    def test_returns_400_for_invalid_reason(self) -> None:
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(self.url, {"reason": "INVALID"})

        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIn("error_detail", data)

    def test_returns_403_for_non_admin(self) -> None:
        self.client.force_authenticate(user=self.normal_user)
        res = self.client.get(self.url, {"reason": Withdrawal.Reason.GRADUATION})

        self.assertEqual(res.status_code, 403)

    def test_returns_401_when_unauthenticated(self) -> None:
        res = self.client.get(self.url, {"reason": Withdrawal.Reason.GRADUATION})

        self.assertEqual(res.status_code, 401)
