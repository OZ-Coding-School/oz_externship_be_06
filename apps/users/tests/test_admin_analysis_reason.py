from typing import Any,cast

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models.withdrawal import Withdrawal


User = get_user_model()


class AdminAnalysisReasonTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # 테스트 데이터 (모든 테스트에서 공유, 성능 좋음)
        Withdrawal.objects.create(reason="LACK_OF_CONTENT", created_at=timezone.now())
        Withdrawal.objects.create(reason="LACK_OF_CONTENT", created_at=timezone.now())
        Withdrawal.objects.create(reason="EXPENSIVE", created_at=timezone.now())

        # 관리자 유저 생성 (프로젝트 User 필드에 맞게 수정)
        cls.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            name="관리자",
            nickname="관리자",
            phone_number="01011111111",
            gender=User.Gender.MALE,
            birthday=timezone.now().date(),
            role=User.Role.ADMIN,
            is_active=True,
        )

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=cast(Any, self).admin_user)

    def test_get_monthly_withdrawal_stats_service(self) -> None:
        from apps.users.services.admin_analysis_reason_service import AdminAnalysisReasonService

        service = AdminAnalysisReasonService()
        result = service.get_monthly_withdrawal_stats("LACK_OF_CONTENT")

        self.assertEqual(result["reason"], "LACK_OF_CONTENT")
        self.assertEqual(result["total"], 2)
        self.assertTrue(len(result["items"]) > 0)

    def test_withdrawal_reason_stats_view_admin_only(self) -> None:
        url = reverse("admin-withdrawal-stats")
        response = self.client.get(url, {"reason": "LACK_OF_CONTENT"})
        data = cast(Any, response).data
        self.assertIn("items", data)

    def test_withdrawal_reason_stats_view_invalid_reason(self) -> None:
        url = reverse("admin-withdrawal-stats")
        response = self.client.get(url, {"reason": "INVALID_CODE"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)