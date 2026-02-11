from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.courses.models import Cohort, Course
from apps.courses.models.cohort_students import CohortStudent
from apps.users.models import User


class AvailableCoursesAPITests(TestCase):
    client: APIClient

    url: str
    user: User
    course_backend: Course
    course_frontend: Course
    cohort_backend_1: Cohort
    cohort_backend_2: Cohort
    cohort_backend_in_progress: Cohort
    cohort_frontend_1: Cohort

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = "/api/v1/accounts/available-courses"

        cls.user = User.objects.create_user(
            email="course_test@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="테스터",
            nickname="tester",
            gender="MALE",
            is_active=True,
        )

        cls.course_backend = Course.objects.create(
            name="백엔드 과정",
            tag="BE",
            description="백엔드 부트캠프",
        )

        cls.course_frontend = Course.objects.create(
            name="프론트엔드 과정",
            tag="FE",
            description="프론트엔드 부트캠프",
        )

        cls.cohort_backend_1 = Cohort.objects.create(
            course=cls.course_backend,
            number=1,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
            status=Cohort.StatusChoices.PREPARING,
        )

        cls.cohort_backend_2 = Cohort.objects.create(
            course=cls.course_backend,
            number=2,
            max_student=30,
            start_date=date(2025, 7, 1),
            end_date=date(2025, 12, 31),
            status=Cohort.StatusChoices.PREPARING,
        )

        cls.cohort_backend_in_progress = Cohort.objects.create(
            course=cls.course_backend,
            number=3,
            max_student=30,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            status=Cohort.StatusChoices.IN_PROGRESS,
        )

        cls.cohort_frontend_1 = Cohort.objects.create(
            course=cls.course_frontend,
            number=4,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
            status=Cohort.StatusChoices.PREPARING,
        )

    def setUp(self) -> None:
        self.client = APIClient()
        access = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_available_courses_nested_structure_success_200(self) -> None:
        """과정별 기수가 중첩 구조로 반환되는지 확인"""
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

        # 과정 이름 확인
        course_names = [item["course"]["name"] for item in data]
        self.assertIn("백엔드 과정", course_names)
        self.assertIn("프론트엔드 과정", course_names)

    def test_available_courses_backend_cohorts_200(self) -> None:
        """백엔드 과정에 PREPARING 상태의 기수만 포함되는지 확인"""
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()

        backend_data = next(item for item in data if item["course"]["name"] == "백엔드 과정")
        cohort_numbers = [cohort["number"] for cohort in backend_data["cohorts"]]

        self.assertEqual(len(backend_data["cohorts"]), 2)
        self.assertIn(1, cohort_numbers)
        self.assertIn(2, cohort_numbers)
        self.assertNotIn(3, cohort_numbers)  # IN_PROGRESS 상태는 제외

    def test_available_courses_frontend_cohorts_200(self) -> None:
        """프론트엔드 과정의 기수가 올바르게 반환되는지 확인"""
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()

        frontend_data = next(item for item in data if item["course"]["name"] == "프론트엔드 과정")

        self.assertEqual(len(frontend_data["cohorts"]), 1)
        self.assertEqual(frontend_data["cohorts"][0]["number"], 4)

    def test_available_courses_unauthenticated_401(self) -> None:
        self.client.credentials()

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class EnrolledCoursesAPITests(TestCase):
    client: APIClient

    url: str
    user: User
    course: Course
    cohort: Cohort

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = "/api/v1/accounts/me/enrolled-courses"

        cls.user = User.objects.create_user(
            email="enrolled_test@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345679",
            name="테스터2",
            nickname="tester2",
            gender="MALE",
            is_active=True,
        )

        cls.course = Course.objects.create(
            name="프론트엔드 과정",
            tag="FE",
            description="프론트엔드 부트캠프",
        )

        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
            status=Cohort.StatusChoices.IN_PROGRESS,
        )

        CohortStudent.objects.create(user=cls.user, cohort=cls.cohort)

    def setUp(self) -> None:
        self.client = APIClient()
        access = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_enrolled_courses_success_200(self) -> None:
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["cohort"]["id"], self.cohort.id)
        self.assertEqual(data[0]["course"]["name"], "프론트엔드 과정")
        self.assertEqual(data[0]["course"]["tag"], "FE")

    def test_enrolled_courses_empty_list_200(self) -> None:
        CohortStudent.objects.filter(user=self.user).delete()

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data, [])

    def test_enrolled_courses_unauthenticated_401(self) -> None:
        self.client.credentials()

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
