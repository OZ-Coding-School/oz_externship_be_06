from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.courses.models import Cohort, Course
from apps.users.models import StudentEnrollmentRequest


class EnrollStudentAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/accounts/enroll-student/"

        User = get_user_model()
        self.user = User.objects.create_user(
            email="enroll_test@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="테스터",
            nickname="tester",
            gender="MALE",
            role="USER",
            is_active=True,
        )

        self.course = Course.objects.create(
            name="백엔드 과정",
            tag="BE",
            description="백엔드 부트캠프",
        )

        self.cohort = Cohort.objects.create(
            course=self.course,
            number=1,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
            status=Cohort.StatusChoices.PREPARING,
        )

        access = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_enroll_student_success_201(self) -> None:
        res = self.client.post(
            self.url,
            {"cohort_id": self.cohort.id},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data = res.json()
        self.assertIn("detail", data)
        self.assertTrue(StudentEnrollmentRequest.objects.filter(user=self.user, cohort=self.cohort).exists())

    def test_enroll_student_invalid_cohort_400(self) -> None:
        res = self.client.post(
            self.url,
            {"cohort_id": 99999},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enroll_student_already_enrolled_409(self) -> None:
        StudentEnrollmentRequest.objects.create(
            user=self.user,
            cohort=self.cohort,
            status=StudentEnrollmentRequest.Status.PENDING,
        )

        res = self.client.post(
            self.url,
            {"cohort_id": self.cohort.id},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)

    def test_enroll_student_not_user_role_403(self) -> None:
        self.user.role = "STUDENT"
        self.user.save()

        res = self.client.post(
            self.url,
            {"cohort_id": self.cohort.id},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_enroll_student_unauthenticated_401(self) -> None:
        self.client.credentials()

        res = self.client.post(
            self.url,
            {"cohort_id": self.cohort.id},
            format="json",
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
