from datetime import date, timedelta
from typing import Any

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models import Cohort, CohortStudent, Course
from apps.users.models import User


class AdminStudentListAPITest(TestCase):
    """어드민 수강생 목록 조회 API 테스트."""

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
        self.cohort_be_2 = Cohort.objects.create(
            course=self.course_be,
            number=2,
            max_student=30,
            start_date=date.today() + timedelta(days=200),
            end_date=date.today() + timedelta(days=380),
            status=Cohort.StatusChoices.PREPARING,
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

        # 수강생 유저들
        self.student1 = User.objects.create_user(
            email="student1@example.com",
            password="password123",
            name="김수강",
            nickname="수강생1",
            phone_number="01033333333",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.STUDENT,
        is_active=True,
        )
        CohortStudent.objects.create(user=self.student1, cohort=self.cohort_be_1)

        self.student2 = User.objects.create_user(
            email="student2@example.com",
            password="password123",
            name="이수강",
            nickname="수강생2",
            phone_number="01044444444",
            gender=User.Gender.FEMALE,
            birthday=date(2001, 2, 2),
            role=User.Role.STUDENT,
        is_active=True,
        )
        CohortStudent.objects.create(user=self.student2, cohort=self.cohort_be_2)

        self.student3 = User.objects.create_user(
            email="student3@example.com",
            password="password123",
            name="박수강",
            nickname="수강생3",
            phone_number="01055555555",
            gender=User.Gender.MALE,
            birthday=date(2002, 3, 3),
            role=User.Role.STUDENT,
        is_active=True,
        )
        CohortStudent.objects.create(user=self.student3, cohort=self.cohort_fe_1)

        # 비활성화된 수강생
        self.inactive_student = User.objects.create_user(
            email="inactive@example.com",
            password="password123",
            name="비활성수강생",
            nickname="비활성",
            phone_number="01066666666",
            gender=User.Gender.MALE,
            birthday=date(2000, 4, 4),
            role=User.Role.STUDENT,
            is_active=False,
        )
        CohortStudent.objects.create(user=self.inactive_student, cohort=self.cohort_be_1)

        # 일반 유저
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            name="일반유저",
            nickname="일반유저",
            phone_number="01077777777",
            gender=User.Gender.MALE,
            birthday=date(2000, 5, 5),
            role=User.Role.USER,
        is_active=True,
        )

    def _get_url(self) -> str:
        return "/api/v1/admin/students/"

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_admin_can_list_students(self) -> None:
        """관리자가 수강생 목록을 조회할 수 있다."""
        response = self.client.get(
            self._get_url(),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("count", data)
        self.assertIn("results", data)
        self.assertEqual(data["count"], 4)  # 4명의 수강생

    def test_ta_can_list_students(self) -> None:
        """조교가 수강생 목록을 조회할 수 있다."""
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
        student = data["results"][0]

        required_fields = [
            "id",
            "email",
            "nickname",
            "name",
            "phone_number",
            "birthday",
            "status",
            "role",
            "in_progress_course",
            "created_at",
        ]
        for field in required_fields:
            self.assertIn(field, student)

    def test_in_progress_course_structure(self) -> None:
        """in_progress_course 필드 구조가 올바르다."""
        response = self.client.get(
            self._get_url(),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # 수강 중인 과정이 있는 수강생 찾기
        student_with_course = None
        for student in data["results"]:
            if student["in_progress_course"]:
                student_with_course = student
                break

        self.assertIsNotNone(student_with_course)
        assert student_with_course is not None
        course_info = student_with_course["in_progress_course"]
        self.assertIn("cohort", course_info)
        self.assertIn("course", course_info)
        self.assertIn("id", course_info["cohort"])
        self.assertIn("number", course_info["cohort"])
        self.assertIn("id", course_info["course"])
        self.assertIn("name", course_info["course"])
        self.assertIn("tag", course_info["course"])

    def test_search_by_name(self) -> None:
        """이름으로 검색할 수 있다."""
        response = self.client.get(
            f"{self._get_url()}?search=김수강",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["name"], "김수강")

    def test_search_by_email(self) -> None:
        """이메일로 검색할 수 있다."""
        response = self.client.get(
            f"{self._get_url()}?search=student1@",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)

    def test_filter_by_status_activated(self) -> None:
        """활성화 상태로 필터링할 수 있다."""
        response = self.client.get(
            f"{self._get_url()}?status=activated",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 3)  # 활성화된 수강생 3명

    def test_filter_by_status_deactivated(self) -> None:
        """비활성화 상태로 필터링할 수 있다."""
        response = self.client.get(
            f"{self._get_url()}?status=deactivated",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)  # 비활성화된 수강생 1명

    def test_filter_by_course_id(self) -> None:
        """과정 ID로 필터링할 수 있다."""
        response = self.client.get(
            f"{self._get_url()}?course_id={self.course_be.id}",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 3)  # 백엔드 과정 수강생 3명

    def test_filter_by_cohort_id(self) -> None:
        """기수 ID로 필터링할 수 있다."""
        response = self.client.get(
            f"{self._get_url()}?cohort_id={self.cohort_be_1.id}",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 2)  # BE 1기 수강생 2명

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

    def test_ordered_by_id(self) -> None:
        """ID 순으로 정렬된다."""
        response = self.client.get(
            self._get_url(),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        ids = [student["id"] for student in data["results"]]
        self.assertEqual(ids, sorted(ids))

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
