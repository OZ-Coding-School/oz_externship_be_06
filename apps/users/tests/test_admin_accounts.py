from typing import Any

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User, Withdrawal


class AdminUserListViewTest(APITestCase):
    def setUp(self) -> None:
        """테스트 데이터 설정: birthday 필드 누락 방지"""
        # 1. 어드민 유저 생성
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com", password="password123", nickname="admin", birthday="1990-01-01"
        )
        # 2. 필터 테스트용 일반 유저들 생성
        self.active_user = User.objects.create_user(
            email="active@test.com",
            password="password123",
            nickname="active",
            is_active=True,
            role="USER",
            birthday="1990-01-01",
        )
        self.inactive_user = User.objects.create_user(
            email="inactive@test.com",
            password="password123",
            nickname="inactive",
            is_active=False,
            role="STUDENT",
            birthday="1990-01-01",
        )
        self.withdrawn_user = User.objects.create_user(
            email="withdrew@test.com", password="password123", nickname="withdrew", role="USER", birthday="1990-01-01"
        )
        Withdrawal.objects.create(user=self.withdrawn_user, reason="Test reason")

        self.url = reverse("admin-account-list")

    def test_access_denied_for_normal_user(self) -> None:
        """일반 유저는 권한 없음(403) 응답 확인"""
        self.client.force_authenticate(user=self.active_user)
        response: Any = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "권한이 없습니다.")

    def test_filter_by_status_logic(self) -> None:
        """상태 필터링 로직 실행"""
        self.client.force_authenticate(user=self.admin_user)

        # 탈퇴 회원 필터
        res_withdrew: Any = self.client.get(self.url, {"status": "withdrew"})
        self.assertEqual(res_withdrew.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_withdrew.data["results"]), 1)

    def test_filter_by_individual_role_logic(self) -> None:
        """피드백 반영: TA, OM, LC 개별 역할 필터링 테스트"""
        self.client.force_authenticate(user=self.admin_user)

        # 개별 역할 유저 추가 생성
        User.objects.create_user(email="ta@test.com", password="password123", role="TA", birthday="1990-01-01")
        User.objects.create_user(email="om@test.com", password="password123", role="OM", birthday="1990-01-01")

        # 1. TA 필터 확인 (시리얼라이저가 소문자로 반환하므로 .lower()와 비교)
        response_ta: Any = self.client.get(self.url, {"role": "ta"})
        self.assertEqual(response_ta.status_code, status.HTTP_200_OK)
        self.assertEqual(response_ta.data["results"][0]["role"].lower(), "ta")

        # 2. OM 필터 확인
        response_om: Any = self.client.get(self.url, {"role": "om"})
        self.assertEqual(response_om.data["results"][0]["role"].lower(), "om")

    def test_search_and_exception_handling(self) -> None:
        """검색 로직 및 401 인증 예외 처리 커버"""
        # 1. 인증 없이 요청
        response_401: Any = self.client.get(self.url)
        self.assertEqual(response_401.status_code, status.HTTP_401_UNAUTHORIZED)

        # 2. 검색어 필터 실행
        self.client.force_authenticate(user=self.admin_user)
        # 검색 결과 중 nickname에 'active'가 포함된 데이터가 있는지 확인 (인덱스 순서 영향 제거)
        response_search: Any = self.client.get(self.url, {"search": "active"})
        self.assertEqual(response_search.status_code, status.HTTP_200_OK)

        nicknames = [item["nickname"] for item in response_search.data["results"]]
        self.assertIn("active", nicknames)