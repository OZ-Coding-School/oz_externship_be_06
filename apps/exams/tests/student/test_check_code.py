from __future__ import annotations

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.courses.models import Cohort, Course, Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam, ExamDeployment
from apps.users.models import User


class CheckCodeAPITest(APITestCase):
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

    def _check_code_url(self) -> str:
        return reverse("exams:check-code", kwargs={"deployment_id": self.deployment.id})

    def test_check_code_success(self) -> None:
        """참가코드 검증 성공 테스트"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self._check_code_url(), {"code": "testcode123"})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_check_code_invalid_code(self) -> None:
        """잘못된 참가코드 테스트"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self._check_code_url(), {"code": "wrongcode"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)
        self.assertIn(ErrorMessages.INVALID_CHECK_CODE_REQUEST.value, str(response.data["error_detail"]))

    def test_check_code_missing_code(self) -> None:
        """참가코드 필드 누락 테스트"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self._check_code_url(), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_code_unauthenticated(self) -> None:
        """인증되지 않은 사용자 테스트"""
        response = self.client.post(self._check_code_url(), {"code": "testcode123"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_check_code_non_student_role(self) -> None:
        """수강생이 아닌 사용자 테스트"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self._check_code_url(), {"code": "testcode123"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error_detail", response.data)
        self.assertIn(ErrorMessages.NO_EXAM_TAKE_PERMISSION.value, str(response.data["error_detail"]))

    def test_check_code_deployment_not_found(self) -> None:
        """존재하지 않는 배포 정보 테스트"""
        self.client.force_authenticate(user=self.student_user)
        url = reverse("exams:check-code", kwargs={"deployment_id": 99999})
        response = self.client.post(url, {"code": "testcode123"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error_detail", response.data)
        self.assertIn(ErrorMessages.DEPLOYMENT_NOT_FOUND.value, str(response.data["error_detail"]))

    def test_check_code_deactivated_status(self) -> None:
        """비활성화된 시험 테스트"""
        self.deployment.status = ExamDeployment.StatusChoices.DEACTIVATED
        self.deployment.save()
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self._check_code_url(), {"code": "testcode123"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)
        self.assertIn(ErrorMessages.INVALID_CHECK_CODE_REQUEST.value, str(response.data["error_detail"]))

    def test_check_code_before_open_time(self) -> None:
        """응시 시작 시간 전 테스트"""
        now = timezone.now()
        self.deployment.open_at = now + timedelta(hours=1)
        self.deployment.close_at = now + timedelta(hours=2)
        self.deployment.save()
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self._check_code_url(), {"code": "testcode123"})
        self.assertEqual(response.status_code, status.HTTP_423_LOCKED)
        self.assertIn("error_detail", response.data)
        self.assertIn(ErrorMessages.EXAM_NOT_AVAILABLE.value, str(response.data["error_detail"]))

    def test_check_code_after_close_time(self) -> None:
        """응시 종료 시간 후 테스트"""
        now = timezone.now()
        self.deployment.open_at = now - timedelta(hours=2)
        self.deployment.close_at = now - timedelta(hours=1)
        self.deployment.save()
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self._check_code_url(), {"code": "testcode123"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)
        self.assertIn(ErrorMessages.EXAM_ALREADY_CLOSED.value, str(response.data["error_detail"]))
