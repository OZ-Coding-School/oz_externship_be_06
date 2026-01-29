from datetime import date
from typing import Any

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import User, Withdrawal


class AdminWithdrawalListAPITest(TestCase):
    """어드민 탈퇴 내역 목록 조회 API 테스트."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/admin/withdrawals/"

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
        is_active=True,
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
        is_active=True,
        )

        # 탈퇴한 학생 유저들
        self.withdrawn_student1 = User.objects.create_user(
            email="student1@example.com",
            password="password123",
            name="김학생",
            nickname="학생1",
            phone_number="01033333333",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.STUDENT,
            is_active=False,
        )
        self.withdrawn_student2 = User.objects.create_user(
            email="student2@example.com",
            password="password123",
            name="이학생",
            nickname="학생2",
            phone_number="01044444444",
            gender=User.Gender.FEMALE,
            birthday=date(2001, 2, 2),
            role=User.Role.STUDENT,
            is_active=False,
        )

        # 탈퇴한 조교 유저
        self.withdrawn_ta = User.objects.create_user(
            email="withdrawn_ta@example.com",
            password="password123",
            name="박조교",
            nickname="조교2",
            phone_number="01055555555",
            gender=User.Gender.MALE,
            birthday=date(1995, 5, 5),
            role=User.Role.TA,
            is_active=False,
        )

        # 탈퇴 내역 생성
        self.withdrawal1 = Withdrawal.objects.create(
            user=self.withdrawn_student1,
            reason=Withdrawal.Reason.GRADUATION,
            reason_detail="수료 완료했습니다.",
        )
        self.withdrawal2 = Withdrawal.objects.create(
            user=self.withdrawn_student2,
            reason=Withdrawal.Reason.NO_LONGER_NEEDED,
            reason_detail="더 이상 필요 없습니다.",
        )
        self.withdrawal3 = Withdrawal.objects.create(
            user=self.withdrawn_ta,
            reason=Withdrawal.Reason.TRANSFER,
            reason_detail="다른 회사로 이직합니다.",
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
        is_active=True,
        )

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_admin_can_get_withdrawal_list(self) -> None:
        """관리자가 탈퇴 내역 목록을 조회할 수 있다."""
        response = self.client.get(self.url, **self._auth_headers(self.admin_user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 3)

    def test_ta_can_get_withdrawal_list(self) -> None:
        """조교가 탈퇴 내역 목록을 조회할 수 있다."""
        response = self.client.get(self.url, **self._auth_headers(self.ta_user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_format(self) -> None:
        """응답 형식이 명세서와 일치한다."""
        response = self.client.get(self.url, **self._auth_headers(self.admin_user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # 페이지네이션 필드 확인
        self.assertIn("count", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)
        self.assertIn("results", data)

        # 목록 항목 필드 확인
        item = data["results"][0]
        self.assertIn("id", item)
        self.assertIn("user", item)
        self.assertIn("reason", item)
        self.assertIn("reason_display", item)
        self.assertIn("withdrawn_at", item)

        # 유저 정보 필드 확인
        user_info = item["user"]
        self.assertIn("id", user_info)
        self.assertIn("email", user_info)
        self.assertIn("name", user_info)
        self.assertIn("role", user_info)
        self.assertIn("birthday", user_info)

    def test_search_by_email(self) -> None:
        """이메일로 검색할 수 있다."""
        response = self.client.get(
            self.url,
            {"search": "student1"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["user"]["email"], "student1@example.com")

    def test_search_by_name(self) -> None:
        """이름으로 검색할 수 있다."""
        response = self.client.get(
            self.url,
            {"search": "김학생"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["user"]["name"], "김학생")

    def test_filter_by_role_student(self) -> None:
        """학생 권한으로 필터링할 수 있다."""
        response = self.client.get(
            self.url,
            {"role": "student"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data["results"]), 2)
        for item in data["results"]:
            self.assertEqual(item["user"]["role"], "STUDENT")

    def test_filter_by_role_ta(self) -> None:
        """조교 권한으로 필터링할 수 있다."""
        response = self.client.get(
            self.url,
            {"role": "training_assistant"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["user"]["role"], "TA")

    def test_sort_by_latest(self) -> None:
        """최신순으로 정렬할 수 있다."""
        response = self.client.get(
            self.url,
            {"sort": "latest"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # 가장 최근 생성된 것이 첫 번째
        self.assertEqual(data["results"][0]["id"], self.withdrawal3.id)

    def test_sort_by_oldest(self) -> None:
        """오래된순으로 정렬할 수 있다."""
        response = self.client.get(
            self.url,
            {"sort": "oldest"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # 가장 오래된 것이 첫 번째
        self.assertEqual(data["results"][0]["id"], self.withdrawal1.id)

    def test_pagination(self) -> None:
        """페이지네이션이 동작한다."""
        response = self.client.get(
            self.url,
            {"page_size": 2},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["count"], 3)
        self.assertIsNotNone(data["next"])

    def test_returns_401_when_unauthenticated(self) -> None:
        """인증되지 않은 사용자는 401을 받는다."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_403_for_normal_user(self) -> None:
        """일반 유저는 403을 받는다."""
        response = self.client.get(self.url, **self._auth_headers(self.normal_user))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reason_display_is_korean(self) -> None:
        """탈퇴 사유가 한글로 표시된다."""
        response = self.client.get(self.url, **self._auth_headers(self.admin_user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # GRADUATION 사유를 가진 항목 찾기
        graduation_item = next((item for item in data["results"] if item["reason"] == "GRADUATION"), None)
        assert graduation_item is not None
        self.assertEqual(graduation_item["reason_display"], "졸업 및 수료")
