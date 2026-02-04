from typing import Any

import pytest  # type: ignore
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.users.models.withdrawal import Withdrawal


@pytest.mark.django_db
class TestAdminAnalysisReason:
    @pytest.fixture  # type: ignore
    def setup_data(self) -> None:  # -> None 추가
        # 1. 테스트용 데이터 생성
        Withdrawal.objects.create(reason="LACK_OF_CONTENT", created_at=timezone.now())
        Withdrawal.objects.create(reason="LACK_OF_CONTENT", created_at=timezone.now())
        Withdrawal.objects.create(reason="EXPENSIVE", created_at=timezone.now())

    def test_get_monthly_withdrawal_stats_service(self, setup_data: Any) -> None:  # 인자 및 반환 타입 추가
        from apps.users.services.admin_analysis_reason_service import (
            AdminAnalysisReasonService,
        )

        service = AdminAnalysisReasonService()
        result = service.get_monthly_withdrawal_stats("LACK_OF_CONTENT")

        # 서비스 로직 검증
        assert result["reason"] == "LACK_OF_CONTENT"
        assert result["total"] == 2
        assert len(result["items"]) > 0

    def test_withdrawal_reason_stats_view_admin_only(self, admin_client: Any) -> None:  # 인자 및 반환 타입 추가
        # 2. 어드민 권한으로 API 접근 테스트
        # URL name이 'admin-withdrawal-stats'로 admin_urls.py에 정의되어 있어야 함
        url = reverse("admin-withdrawal-stats")
        response = admin_client.get(f"{url}?reason=LACK_OF_CONTENT")

        assert response.status_code == status.HTTP_200_OK
        assert "items" in response.data

    def test_withdrawal_reason_stats_view_invalid_reason(self, admin_client: Any) -> None:  # 인자 및 반환 타입 추가
        # 3. 잘못된 사유 코드 입력 시 에러 처리 테스트
        url = reverse("admin-withdrawal-stats")
        response = admin_client.get(f"{url}?reason=INVALID_CODE")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error_detail" in response.data
