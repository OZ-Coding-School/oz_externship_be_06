from datetime import date, datetime
from typing import Any

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohort_students import CohortStudent
from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.users.models import User


class AdminStudentEnrollmentTrendsAPITest(TestCase):
    """어드민 수강 등록 추세 분석 API 테스트."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/admin/analytics/student-enrollments/trends/"

        # 관리자 유저
        self.admin_user = User.objects.create_user(
            email="admin_enroll@example.com",
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
            email="ta_enroll@example.com",
            password="password123",
            name="조교",
            nickname="조교",
            phone_number="01022222222",
            gender=User.Gender.FEMALE,
            birthday=date(1995, 5, 5),
            role=User.Role.TA,
            is_active=True,
        )

        # 러닝코치 유저
        self.lc_user = User.objects.create_user(
            email="lc_enroll@example.com",
            password="password123",
            name="러닝코치",
            nickname="러닝코치",
            phone_number="01033333333",
            gender=User.Gender.MALE,
            birthday=date(1992, 3, 3),
            role=User.Role.LC,
            is_active=True,
        )

        # 운영매니저 유저
        self.om_user = User.objects.create_user(
            email="om_enroll@example.com",
            password="password123",
            name="운영매니저",
            nickname="운영매니저",
            phone_number="01044444444",
            gender=User.Gender.FEMALE,
            birthday=date(1993, 4, 4),
            role=User.Role.OM,
            is_active=True,
        )

        # 일반 유저 (권한 없음)
        self.normal_user = User.objects.create_user(
            email="normal_enroll@example.com",
            password="password123",
            name="일반유저",
            nickname="일반유저",
            phone_number="01077777777",
            gender=User.Gender.MALE,
            birthday=date(2000, 5, 5),
            role=User.Role.USER,
            is_active=True,
        )

        # 수강생 유저들 (CohortStudent 데이터용)
        self.student1 = User.objects.create_user(
            email="student1@example.com",
            password="password123",
            name="수강생1",
            nickname="수강생1",
            phone_number="01081111111",
            gender=User.Gender.MALE,
            birthday=date(1998, 1, 1),
            role=User.Role.STUDENT,
            is_active=True,
        )
        self.student2 = User.objects.create_user(
            email="student2@example.com",
            password="password123",
            name="수강생2",
            nickname="수강생2",
            phone_number="01082222222",
            gender=User.Gender.FEMALE,
            birthday=date(1999, 2, 2),
            role=User.Role.STUDENT,
            is_active=True,
        )
        self.student3 = User.objects.create_user(
            email="student3@example.com",
            password="password123",
            name="수강생3",
            nickname="수강생3",
            phone_number="01083333333",
            gender=User.Gender.MALE,
            birthday=date(2000, 3, 3),
            role=User.Role.STUDENT,
            is_active=True,
        )

        # Course 및 Cohort 생성
        self.course = Course.objects.create(
            name="테스트 강좌",
            tag="TST",
            description="테스트용 강좌입니다.",
        )

        today = date.today()
        self.current_year = today.year
        self.prev_year = today.year - 1

        self.cohort = Cohort.objects.create(
            course=self.course,
            number=1,
            max_student=30,
            start_date=date(self.current_year, 1, 1),
            end_date=date(self.current_year, 6, 30),
            status=Cohort.StatusChoices.IN_PROGRESS,
        )

        # CohortStudent 데이터 생성 (연도/월 분산)
        self.cs1 = CohortStudent.objects.create(user=self.student1, cohort=self.cohort)
        self.cs2 = CohortStudent.objects.create(user=self.student2, cohort=self.cohort)
        self.cs3 = CohortStudent.objects.create(user=self.student3, cohort=self.cohort)

        # created_at 날짜 수동 설정
        CohortStudent.objects.filter(id=self.cs1.id).update(
            created_at=timezone.make_aware(datetime(self.prev_year, 11, 10, 10, 0, 0))
        )
        CohortStudent.objects.filter(id=self.cs2.id).update(
            created_at=timezone.make_aware(datetime(self.prev_year, 12, 15, 10, 0, 0))
        )
        CohortStudent.objects.filter(id=self.cs3.id).update(
            created_at=timezone.make_aware(datetime(self.current_year, 1, 20, 10, 0, 0))
        )

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    # ===== 성공 케이스 =====

    def test_admin_can_get_monthly_trends(self) -> None:
        """관리자가 월별 수강 등록 추세를 조회할 수 있다."""
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
        """관리자가 특정 연도의 월별 수강 등록 추세를 조회할 수 있다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly", "year": str(self.current_year)},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["interval"], "monthly")
        self.assertEqual(data["from_date"], f"{self.current_year}-01-01")
        self.assertEqual(data["to_date"], f"{self.current_year}-12-31")
        self.assertEqual(len(data["items"]), 12)

        # 첫 번째 항목은 1월
        self.assertEqual(data["items"][0]["period"], f"{self.current_year}-01")
        # 마지막 항목은 12월
        self.assertEqual(data["items"][11]["period"], f"{self.current_year}-12")

    def test_admin_can_get_yearly_trends(self) -> None:
        """관리자가 년별 수강 등록 추세를 조회할 수 있다."""
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

    def test_ta_can_get_trends(self) -> None:
        """조교가 수강 등록 추세를 조회할 수 있다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly"},
            **self._auth_headers(self.ta_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lc_can_get_trends(self) -> None:
        """러닝코치가 수강 등록 추세를 조회할 수 있다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly"},
            **self._auth_headers(self.lc_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_om_can_get_trends(self) -> None:
        """운영매니저가 수강 등록 추세를 조회할 수 있다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly"},
            **self._auth_headers(self.om_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ===== 응답 형식 검증 =====

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

        for item in data["items"]:
            self.assertRegex(item["period"], r"^\d{4}$")

    def test_total_equals_sum_of_counts(self) -> None:
        """total이 items의 count 합계와 일치한다."""
        response = self.client.get(
            self.url,
            {"interval": "yearly"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        expected_total = sum(item["count"] for item in data["items"])
        self.assertEqual(data["total"], expected_total)

    def test_monthly_items_ordered_by_month(self) -> None:
        """월별 items가 1월부터 12월 순서로 정렬된다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly", "year": str(self.current_year)},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        periods = [item["period"] for item in data["items"]]
        expected = [f"{self.current_year}-{m:02d}" for m in range(1, 13)]
        self.assertEqual(periods, expected)

    # ===== 데이터 검증 =====

    def test_counts_enrollments_in_specific_month(self) -> None:
        """특정 월의 수강 등록 수가 정확하게 집계된다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly", "year": str(self.current_year)},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # 1월에 cs3가 등록됨
        jan_period = f"{self.current_year}-01"
        jan_item = next((item for item in data["items"] if item["period"] == jan_period), None)
        assert jan_item is not None
        self.assertGreaterEqual(jan_item["count"], 1)

    def test_counts_enrollments_in_prev_year(self) -> None:
        """이전 연도의 수강 등록 수가 정확하게 집계된다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly", "year": str(self.prev_year)},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # 11월에 cs1, 12월에 cs2가 등록됨
        nov_period = f"{self.prev_year}-11"
        nov_item = next((item for item in data["items"] if item["period"] == nov_period), None)
        assert nov_item is not None
        self.assertGreaterEqual(nov_item["count"], 1)

        dec_period = f"{self.prev_year}-12"
        dec_item = next((item for item in data["items"] if item["period"] == dec_period), None)
        assert dec_item is not None
        self.assertGreaterEqual(dec_item["count"], 1)

    def test_yearly_counts_multiple_years(self) -> None:
        """연도별 조회 시 여러 연도의 데이터가 정확하게 집계된다."""
        response = self.client.get(
            self.url,
            {"interval": "yearly"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # prev_year: cs1, cs2 (2건)
        prev_year_item = next((item for item in data["items"] if item["period"] == str(self.prev_year)), None)
        assert prev_year_item is not None
        self.assertEqual(prev_year_item["count"], 2)

        # current_year: cs3 (1건)
        current_year_item = next((item for item in data["items"] if item["period"] == str(self.current_year)), None)
        assert current_year_item is not None
        self.assertEqual(current_year_item["count"], 1)

    # ===== 실패 케이스 =====

    def test_returns_400_without_interval(self) -> None:
        """interval 없이 요청하면 400을 받는다."""
        response = self.client.get(
            self.url,
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.json())

    def test_returns_400_with_invalid_interval(self) -> None:
        """잘못된 interval로 요청하면 400을 받는다."""
        response = self.client.get(
            self.url,
            {"interval": "weekly"},
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get("error_detail"), "잘못된 요청입니다.")

    def test_returns_401_when_unauthenticated(self) -> None:
        """인증되지 않은 사용자는 401을 받는다."""
        response = self.client.get(self.url, {"interval": "monthly"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.json().get("error_detail"),
            "자격 인증 데이터가 제공되지 않았습니다.",
        )

    def test_returns_403_for_normal_user(self) -> None:
        """일반 유저는 403을 받는다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly"},
            **self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("error_detail"), "권한이 없습니다.")

    def test_returns_403_for_student_user(self) -> None:
        """수강생 유저는 403을 받는다."""
        response = self.client.get(
            self.url,
            {"interval": "monthly"},
            **self._auth_headers(self.student1),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("error_detail"), "권한이 없습니다.")
