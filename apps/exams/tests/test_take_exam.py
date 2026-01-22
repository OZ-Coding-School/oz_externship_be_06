from __future__ import annotations

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.courses.models import Cohort, Course, Subject
from apps.exams.models import Exam, ExamDeployment, ExamSubmission
from apps.users.models import User


class TakeExamAPITest(APITestCase):
    def setUp(self) -> None:
        """테스트 데이터 설정"""
        self.take_exam_url = reverse("exams:take-exam")

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

        # Course, Subject, Cohort 생성
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

        # Exam 생성
        self.exam = Exam.objects.create(
            title="테스트 시험",
            thumbnail_img_url="https://example.com/thumb.jpg",
            subject=self.subject,
        )

        # ExamDeployment 생성 (활성화, 응시 가능 시간 내)
        now = timezone.now()
        self.deployment = ExamDeployment.objects.create(
            exam=self.exam,
            cohort=self.cohort,
            duration_time=60,
            access_code="testcode123",
            open_at=now - timedelta(hours=1),
            close_at=now + timedelta(hours=1),
            questions_snapshot_json={"questions": []},
            status=ExamDeployment.StatusChoices.ACTIVATED,
        )

    def test_take_exam_success(self) -> None:
        """응시 성공 테스트"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self.take_exam_url, {"access_code": "testcode123"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("submission_id", response.data)
        self.assertIn("deployment_id", response.data)
        self.assertIn("exam_id", response.data)
        self.assertEqual(response.data["exam_id"], self.exam.id)
        self.assertEqual(response.data["deployment_id"], self.deployment.id)

        # DB에 submission이 생성되었는지 확인
        submission = ExamSubmission.objects.get(submitter=self.student_user, deployment=self.deployment)
        self.assertEqual(submission.deployment, self.deployment)

    def test_take_exam_invalid_access_code(self) -> None:
        """잘못된 참가코드 테스트"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self.take_exam_url, {"access_code": "invalid_code"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertIn("참가 코드가 올바르지 않습니다", str(response.data["detail"]))

    def test_take_exam_missing_access_code(self) -> None:
        """참가코드 필드 누락 테스트"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self.take_exam_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("access_code", response.data)

    def test_take_exam_non_student_role(self) -> None:
        """수강생이 아닌 사용자 테스트"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.take_exam_url, {"access_code": "testcode123"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertIn("수강생 권한이 필요합니다", str(response.data["detail"]))

    def test_take_exam_unauthenticated(self) -> None:
        """인증되지 않은 사용자 테스트"""
        response = self.client.post(self.take_exam_url, {"access_code": "testcode123"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_take_exam_deactivated_status(self) -> None:
        """비활성화된 시험 테스트"""
        self.deployment.status = ExamDeployment.StatusChoices.DEACTIVATED
        self.deployment.save()

        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self.take_exam_url, {"access_code": "testcode123"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertIn("현재 응시할 수 없는 시험입니다", str(response.data["detail"]))

    def test_take_exam_before_open_time(self) -> None:
        """응시 시작 시간 전 테스트"""
        now = timezone.now()
        self.deployment.open_at = now + timedelta(hours=1)
        self.deployment.close_at = now + timedelta(hours=2)
        self.deployment.save()

        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self.take_exam_url, {"access_code": "testcode123"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertIn("응시 가능 시간이 아닙니다", str(response.data["detail"]))

    def test_take_exam_after_close_time(self) -> None:
        """응시 종료 시간 후 테스트"""
        now = timezone.now()
        self.deployment.open_at = now - timedelta(hours=2)
        self.deployment.close_at = now - timedelta(hours=1)
        self.deployment.save()

        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self.take_exam_url, {"access_code": "testcode123"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertIn("응시 가능 시간이 아닙니다", str(response.data["detail"]))

    def test_take_exam_existing_submission(self) -> None:
        """이미 응시한 경우 기존 submission 반환 테스트"""
        self.client.force_authenticate(user=self.student_user)

        # 첫 번째 응시
        response1 = self.client.post(self.take_exam_url, {"access_code": "testcode123"}, format="json")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        submission_id_1 = response1.data["submission_id"]

        # 두 번째 응시 (같은 사용자, 같은 deployment)
        response2 = self.client.post(self.take_exam_url, {"access_code": "testcode123"}, format="json")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        submission_id_2 = response2.data["submission_id"]

        # 같은 submission이 반환되어야 함
        self.assertEqual(submission_id_1, submission_id_2)
        self.assertEqual(
            ExamSubmission.objects.filter(submitter=self.student_user, deployment=self.deployment).count(), 1
        )
