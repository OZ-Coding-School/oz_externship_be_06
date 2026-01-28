from datetime import date, timedelta
from typing import Any

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models import Cohort, Course
from apps.users.models import User
from apps.users.models.enrollment import StudentEnrollmentRequest


class AdminStudentEnrollmentListAPITest(TestCase):
    """어드민 수강생 등록 요청 목록 조회 API 테스트."""

    def setUp(self) -> None:
        self.client = APIClient()

        # 과정 생성
        self.course_be = Course.objects.create(
            name="백엔드 부트캠프",
            tag="BE",
            description="백엔드 과정",
            thumbnail_img_url="https://example.com/be.png",
        )
        self.course_fe = Course.objects.create(
            name="프론트엔드 부트캠프",
            tag="FE",
            description="프론트엔드 과정",
            thumbnail_img_url="https://example.com/fe.png",
        )

        # 기수 생성
        self.cohort_be_1 = Cohort.objects.create(
            course=self.course_be,
            number=1,
            max_student=30,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=180),
            status=Cohort.StatusChoices.IN_PROGRESS,
        )
        self.cohort_fe_1 = Cohort.objects.create(
            course=self.course_fe,
            number=1,
            max_student=30,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=180),
            status=Cohort.StatusChoices.IN_PROGRESS,
        )

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

        # 일반 유저들 (등록 요청자)
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="password123",
            name="김신청",
            nickname="신청자1",
            phone_number="01033333333",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.USER,
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="password123",
            name="이신청",
            nickname="신청자2",
            phone_number="01044444444",
            gender=User.Gender.FEMALE,
            birthday=date(2001, 2, 2),
            role=User.Role.USER,
        )
        self.user3 = User.objects.create_user(
            email="user3@example.com",
            password="password123",
            name="박신청",
            nickname="신청자3",
            phone_number="01055555555",
            gender=User.Gender.MALE,
            birthday=date(2002, 3, 3),
            role=User.Role.USER,
        )

        # 등록 요청 생성
        self.enrollment1 = StudentEnrollmentRequest.objects.create(
            user=self.user1,
            cohort=self.cohort_be_1,
            status=StudentEnrollmentRequest.Status.PENDING,
        )
        self.enrollment2 = StudentEnrollmentRequest.objects.create(
            user=self.user2,
            cohort=self.cohort_be_1,
            status=StudentEnrollmentRequest.Status.APPROVED,
        )
        self.enrollment3 = StudentEnrollmentRequest.objects.create(
            user=self.user3,
            cohort=self.cohort_fe_1,
            status=StudentEnrollmentRequest.Status.REJECTED,
        )

        # 일반 유저
        self.normal_user = User.objects.create_user(
            email="normal@example.com",
            password="password123",
            name="일반유저",
            nickname="일반유저",
            phone_number="01066666666",
            gender=User.Gender.MALE,
            birthday=date(2000, 5, 5),
            role=User.Role.USER,
        )

    def _get_url(self) -> str:
        return "/api/v1/admin/student-enrollments/"

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_admin_can_list_enrollments(self) -> None:
        """관리자가 수강생 등록 요청 목록을 조회할 수 있다."""
        response = self.client.get(
            self._get_url(),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("count", data)
        self.assertIn("results", data)
        self.assertEqual(data["count"], 3)

    def test_ta_can_list_enrollments(self) -> None:
        """조교가 수강생 등록 요청 목록을 조회할 수 있다."""
        response = self.client.get(
            self._get_url(),
            **self._auth_headers(self.ta_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_contains_required_fields(self) -> None:
        """응답에 필수 필드가 포함되어 있다."""
        response = self.client.get(
            self._get_url(),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        enrollment = data["results"][0]

        self.assertIn("id", enrollment)
        self.assertIn("user", enrollment)
        self.assertIn("cohort", enrollment)
        self.assertIn("course", enrollment)
        self.assertIn("status", enrollment)
        self.assertIn("created_at", enrollment)

        # user 필드 확인
        user = enrollment["user"]
        self.assertIn("id", user)
        self.assertIn("email", user)
        self.assertIn("name", user)
        self.assertIn("birthday", user)
        self.assertIn("gender", user)

        # cohort 필드 확인
        cohort = enrollment["cohort"]
        self.assertIn("id", cohort)
        self.assertIn("number", cohort)

        # course 필드 확인
        course = enrollment["course"]
        self.assertIn("id", course)
        self.assertIn("name", course)
        self.assertIn("tag", course)

    def test_search_by_name(self) -> None:
        """이름으로 검색할 수 있다."""
        response = self.client.get(
            f"{self._get_url()}?search=김신청",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["user"]["name"], "김신청")

    def test_search_by_email(self) -> None:
        """이메일로 검색할 수 있다."""
        response = self.client.get(
            f"{self._get_url()}?search=user1@",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)

    def test_filter_by_status_pending(self) -> None:
        """대기 상태로 필터링할 수 있다."""
        response = self.client.get(
            f"{self._get_url()}?status=pending",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["status"], "PENDING")

    def test_filter_by_status_accepted(self) -> None:
        """승인 상태로 필터링할 수 있다."""
        response = self.client.get(
            f"{self._get_url()}?status=accepted",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        # 모델은 APPROVED, 응답은 ACCEPTED
        self.assertEqual(data["results"][0]["status"], "ACCEPTED")

    def test_filter_by_status_rejected(self) -> None:
        """거절 상태로 필터링할 수 있다."""
        response = self.client.get(
            f"{self._get_url()}?status=rejected",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["status"], "REJECTED")

    def test_sort_by_id_default(self) -> None:
        """기본 정렬은 ID 순이다."""
        response = self.client.get(
            self._get_url(),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        ids = [enrollment["id"] for enrollment in data["results"]]
        self.assertEqual(ids, sorted(ids))

    def test_sort_by_latest(self) -> None:
        """최신순으로 정렬할 수 있다."""
        response = self.client.get(
            f"{self._get_url()}?sort=latest",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # 마지막에 생성된 것이 먼저 나와야 함
        self.assertEqual(data["results"][0]["id"], self.enrollment3.id)

    def test_sort_by_oldest(self) -> None:
        """오래된순으로 정렬할 수 있다."""
        response = self.client.get(
            f"{self._get_url()}?sort=oldest",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # 먼저 생성된 것이 먼저 나와야 함
        self.assertEqual(data["results"][0]["id"], self.enrollment1.id)

    def test_pagination(self) -> None:
        """페이지네이션이 동작한다."""
        response = self.client.get(
            f"{self._get_url()}?page=1&page_size=2",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data["results"]), 2)
        self.assertIsNotNone(data["next"])

    def test_returns_401_when_unauthenticated(self) -> None:
        """인증되지 않은 사용자는 401을 받는다."""
        response = self.client.get(self._get_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_403_for_normal_user(self) -> None:
        """일반 유저는 403을 받는다."""
        response = self.client.get(
            self._get_url(),
            **self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
