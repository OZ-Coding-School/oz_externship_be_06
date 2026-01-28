from __future__ import annotations

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.courses.models import Cohort, Course, Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam, ExamDeployment, ExamSubmission
from apps.users.models import User


class TakeExamAPITest(APITestCase):
    def setUp(self) -> None:
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123",
            name="테스트 학생",
            nickname="학생",
            phone_number="010-1234-5678",
            gender=User.Gender.MALE,
            birthday="2000-01-01",
            role=User.Role.STUDENT,
        )
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            name="테스트 관리자",
            nickname="관리자",
            phone_number="010-8765-4321",
            gender=User.Gender.MALE,
            birthday="1990-01-01",
            role=User.Role.ADMIN,
        )
        self.course = Course.objects.create(name="테스트 강좌")
        self.subject = Subject.objects.create(
            course=self.course, title="테스트 과목", number_of_days=30, number_of_hours=120
        )
        self.cohort = Cohort.objects.create(
            course=self.course,
            number=1,
            max_student=100,
            start_date="2025-01-01",
            end_date="2025-12-31",
        )
        self.exam = Exam.objects.create(
            title="테스트 시험",
            thumbnail_img_url="https://example.com/thumb.jpg",
            subject=self.subject,
        )
        now = timezone.now()
        self.deployment = ExamDeployment.objects.create(
            exam=self.exam,
            cohort=self.cohort,
            duration_time=60,
            access_code="testcode123",
            open_at=now - timedelta(hours=1),
            close_at=now + timedelta(hours=1),
            questions_snapshot_json=[],
            status=ExamDeployment.StatusChoices.ACTIVATED,
        )

    def _take_exam_url(self) -> str:
        return reverse("exams:take-exam", kwargs={"deployment_id": self.deployment.id})

    def test_take_exam_success(self) -> None:
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self._take_exam_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("exam_id", response.data)
        self.assertIn("exam_name", response.data)
        self.assertIn("duration_time", response.data)
        self.assertIn("elapsed_time", response.data)
        self.assertIn("cheating_count", response.data)
        self.assertIn("questions", response.data)
        self.assertEqual(response.data["exam_id"], self.exam.id)
        self.assertEqual(response.data["exam_name"], self.exam.title)
        self.assertEqual(response.data["duration_time"], 60)
        self.assertIsInstance(response.data["questions"], list)
        submission = ExamSubmission.objects.get(submitter=self.student_user, deployment=self.deployment)
        self.assertEqual(submission.deployment, self.deployment)

    def test_take_exam_non_student_role(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self._take_exam_url())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertIn(ErrorMessages.FORBIDDEN.value, str(response.data["detail"]))

    def test_take_exam_unauthenticated(self) -> None:
        response = self.client.get(self._take_exam_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_take_exam_deactivated_status(self) -> None:
        self.deployment.status = ExamDeployment.StatusChoices.DEACTIVATED
        self.deployment.save()
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self._take_exam_url())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertIn(ErrorMessages.EXAM_NOT_AVAILABLE.value, str(response.data["detail"]))

    def test_take_exam_before_open_time(self) -> None:
        now = timezone.now()
        self.deployment.open_at = now + timedelta(hours=1)
        self.deployment.close_at = now + timedelta(hours=2)
        self.deployment.save()
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self._take_exam_url())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertIn(ErrorMessages.EXAM_NOT_AVAILABLE.value, str(response.data["detail"]))

    def test_take_exam_after_close_time(self) -> None:
        now = timezone.now()
        self.deployment.open_at = now - timedelta(hours=2)
        self.deployment.close_at = now - timedelta(hours=1)
        self.deployment.save()
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self._take_exam_url())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertIn(ErrorMessages.EXAM_CLOSED.value, str(response.data["detail"]))

    def test_take_exam_existing_submission(self) -> None:
        self.client.force_authenticate(user=self.student_user)
        r1 = self.client.get(self._take_exam_url())
        self.assertEqual(r1.status_code, status.HTTP_200_OK)
        r2 = self.client.get(self._take_exam_url())
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ExamSubmission.objects.filter(submitter=self.student_user, deployment=self.deployment).count(),
            1,
        )
