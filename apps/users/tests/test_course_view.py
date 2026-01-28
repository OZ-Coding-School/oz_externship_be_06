from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.courses.models import Cohort, Course
from apps.courses.models.cohort_students import CohortStudent


class AvailableCoursesAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/accounts/available-courses/"

        User = get_user_model()
        self.user = User.objects.create_user(
            email="course_test@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="테스터",
            nickname="tester",
            gender="MALE",
        )

        self.course = Course.objects.create(
            name="백엔드 과정",
            tag="BE",
            description="백엔드 부트캠프",
        )

        self.cohort_preparing = Cohort.objects.create(
            course=self.course,
            number=1,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
            status=Cohort.StatusChoices.PREPARING,
        )

        self.cohort_in_progress = Cohort.objects.create(
            course=self.course,
            number=2,
            max_student=30,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            status=Cohort.StatusChoices.IN_PROGRESS,
        )

        access = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_available_courses_success_200(self) -> None:
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["cohort"]["id"], self.cohort_preparing.id)
        self.assertEqual(data[0]["course"]["name"], "백엔드 과정")

    def test_available_courses_unauthenticated_401(self) -> None:
        self.client.credentials()

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class EnrolledCoursesAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/accounts/me/enrolled-courses/"

        User = get_user_model()
        self.user = User.objects.create_user(
            email="enrolled_test@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345679",
            name="테스터2",
            nickname="tester2",
            gender="MALE",
        )

        self.course = Course.objects.create(
            name="프론트엔드 과정",
            tag="FE",
            description="프론트엔드 부트캠프",
        )

        self.cohort = Cohort.objects.create(
            course=self.course,
            number=1,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
            status=Cohort.StatusChoices.IN_PROGRESS,
        )

        CohortStudent.objects.create(user=self.user, cohort=self.cohort)

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
