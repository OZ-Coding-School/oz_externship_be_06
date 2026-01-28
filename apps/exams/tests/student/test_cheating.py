from datetime import date, timedelta

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam, ExamDeployment, ExamSubmission
from apps.users.models import User


class ExamCheatingUpdateAPITest(TestCase):
    """쪽지시험 부정행위 업데이트 API 테스트."""

    def setUp(self) -> None:
        self.course = Course.objects.create(
            name="코스",
            tag="CS",
            description="설명",
            thumbnail_img_url="course.png",
        )
        self.subject = Subject.objects.create(
            course=self.course,
            title="과목",
            number_of_days=1,
            number_of_hours=1,
            thumbnail_img_url="subject.png",
        )
        self.cohort = Cohort.objects.create(
            course=self.course,
            number=1,
            max_student=10,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )
        self.exam = Exam.objects.create(
            subject=self.subject,
            title="시험",
            thumbnail_img_url="exam.png",
        )
        self.deployment = ExamDeployment.objects.create(
            cohort=self.cohort,
            exam=self.exam,
            duration_time=30,
            access_code="CODE",
            open_at=timezone.now() - timedelta(minutes=5),
            close_at=timezone.now() + timedelta(minutes=30),
            questions_snapshot_json={},
            status=ExamDeployment.StatusChoices.ACTIVATED,
        )
        self.student = User.objects.create_user(
            email="student@example.com",
            password="password123",
            name="학생",
            nickname="닉네임",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.STUDENT,
        )
        self.other_user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            name="사용자",
            nickname="닉네임2",
            phone_number="01000000000",
            gender=User.Gender.FEMALE,
            birthday=date(2000, 1, 2),
            role=User.Role.USER,
        )

    def _auth_headers(self, user: User) -> dict[str, str]:
        token = AccessToken.for_user(user)
        return {"Authorization": f"Bearer {token}"}

    def _cache_key(self) -> str:
        return f"exam:cheating:{self.deployment.id}:{self.student.id}"

    def _clear_cache(self) -> None:
        cache.delete(self._cache_key())

    def test_cheating_increments_count(self) -> None:
        self._clear_cache()
        response = self.client.post(
            f"/api/v1/exams/deployments/{self.deployment.id}/cheating/",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["cheating_count"], 1)
        self.assertEqual(data["exam_status"], "activated")
        self.assertFalse(data["force_submit"])

    def test_cheating_returns_closed_when_reaching_limit(self) -> None:
        self._clear_cache()
        for _ in range(2):
            self.client.post(
                f"/api/v1/exams/deployments/{self.deployment.id}/cheating/",
                headers=self._auth_headers(self.student),
            )

        response = self.client.post(
            f"/api/v1/exams/deployments/{self.deployment.id}/cheating/",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["exam_status"], "closed")
        self.assertTrue(data["force_submit"])

    def test_cheating_creates_submission_when_cache_already_closed(self) -> None:
        cache.set(self._cache_key(), 3, timeout=60)

        response = self.client.post(
            f"/api/v1/exams/deployments/{self.deployment.id}/cheating/",
            data={"answers_json": []},
            content_type="application/json",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["force_submit"])
        self.assertTrue(ExamSubmission.objects.filter(submitter=self.student, deployment=self.deployment).exists())

    def test_cheating_returns_409_when_submission_exists(self) -> None:
        ExamSubmission.objects.create(
            submitter=self.student,
            deployment=self.deployment,
            started_at=timezone.now(),
            cheating_count=3,
            answers_json=[],
        )

        response = self.client.post(
            f"/api/v1/exams/deployments/{self.deployment.id}/cheating/",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.SUBMISSION_ALREADY_SUBMITTED.value)

    def test_cheating_returns_403_for_non_student(self) -> None:
        self._clear_cache()
        response = self.client.post(
            f"/api/v1/exams/deployments/{self.deployment.id}/cheating/",
            headers=self._auth_headers(self.other_user),
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data["detail"], ErrorMessages.FORBIDDEN.value)

    def test_cheating_requires_authentication(self) -> None:
        self._clear_cache()
        response = self.client.post(f"/api/v1/exams/deployments/{self.deployment.id}/cheating/")

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["detail"], ErrorMessages.UNAUTHORIZED.value)

    def test_cheating_returns_404_when_deployment_missing(self) -> None:
        self._clear_cache()
        response = self.client.post(
            "/api/v1/exams/deployments/9999/cheating/",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.EXAM_NOT_FOUND.value)

    def test_cheating_returns_410_when_deactivated(self) -> None:
        self._clear_cache()
        self.deployment.status = ExamDeployment.StatusChoices.DEACTIVATED
        self.deployment.save(update_fields=["status"])

        response = self.client.post(
            f"/api/v1/exams/deployments/{self.deployment.id}/cheating/",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 410)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.EXAM_ALREADY_CLOSED.value)
