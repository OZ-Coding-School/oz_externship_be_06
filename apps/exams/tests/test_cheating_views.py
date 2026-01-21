from datetime import date, datetime, timedelta
from typing import Any, cast

from django.test import TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.models import Exam, ExamDeployment, ExamSubmission
from apps.users.models import User

CourseModel = cast(Any, Course)
SubjectModel = cast(Any, Subject)
CohortModel = cast(Any, Cohort)
ExamModel = cast(Any, Exam)
ExamDeploymentModel = cast(Any, ExamDeployment)
ExamSubmissionModel = cast(Any, ExamSubmission)


class ExamCheatingUpdateAPITest(TestCase):
    """쪽지시험 부정행위 업데이트 API 테스트."""

    def setUp(self) -> None:
        self.course = CourseModel.objects.create(
            name="코스",
            tag="CS",
            description="설명",
            thumbnail_img_url="course.png",
        )
        self.subject = SubjectModel.objects.create(
            course=self.course,
            title="과목",
            number_of_days=1,
            number_of_hours=1,
            thumbnail_img_url="subject.png",
        )
        self.cohort = CohortModel.objects.create(
            course=self.course,
            number=1,
            max_student=10,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )
        self.exam = ExamModel.objects.create(
            subject=self.subject,
            title="시험",
            thumbnail_img_url="exam.png",
        )
        self.deployment = ExamDeploymentModel.objects.create(
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

    def _create_submission(self, started_at: datetime | None = None, cheating_count: int = 0) -> ExamSubmission:
        return cast(
            ExamSubmission,
            ExamSubmissionModel.objects.create(
                submitter=self.student,
                deployment=self.deployment,
                started_at=started_at or timezone.now(),
                cheating_count=cheating_count,
                answers_json={},
                score=0,
                correct_answer_count=0,
            ),
        )

    def _auth_headers(self, user: User) -> dict[str, str]:
        token = AccessToken.for_user(user)
        return {"Authorization": f"Bearer {token}"}

    def test_cheating_increments_count(self) -> None:
        self._create_submission()
        response = self.client.post(
            f"/api/exams/deployments/{self.deployment.id}/cheating/",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["cheating_count"], 1)
        self.assertEqual(data["exam_status"], "activated")
        self.assertFalse(data["force_submit"])

    def test_cheating_returns_closed_when_reaching_limit(self) -> None:
        submission = self._create_submission(cheating_count=2)
        response = self.client.post(
            f"/api/exams/deployments/{self.deployment.id}/cheating/",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["exam_status"], "closed")
        self.assertTrue(data["force_submit"])
        submission.refresh_from_db()
        self.assertEqual(submission.cheating_count, 3)

    def test_cheating_returns_403_for_non_student(self) -> None:
        self._create_submission()
        response = self.client.post(
            f"/api/exams/deployments/{self.deployment.id}/cheating/",
            headers=self._auth_headers(self.other_user),
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data["error_detail"], "권한이 없습니다.")

    def test_cheating_returns_400_without_submission(self) -> None:
        response = self.client.post(
            f"/api/exams/deployments/{self.deployment.id}/cheating/",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], "유효하지 않은 시험 응시 세션입니다.")

    def test_cheating_requires_authentication(self) -> None:
        self._create_submission()

        response = self.client.post(f"/api/exams/deployments/{self.deployment.id}/cheating/")

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_cheating_returns_404_when_deployment_missing(self) -> None:
        self._create_submission()
        response = self.client.post(
            "/api/exams/deployments/9999/cheating/",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error_detail"], "해당 시험 정보를 찾을 수 없습니다.")

    def test_cheating_returns_410_when_time_expired(self) -> None:
        self._create_submission(started_at=timezone.now() - timedelta(minutes=60))
        response = self.client.post(
            f"/api/exams/deployments/{self.deployment.id}/cheating/",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 410)
        data = response.json()
        self.assertEqual(data["error_detail"], "시험이 이미 종료되었습니다.")

    def test_cheating_returns_410_when_deactivated(self) -> None:
        self._create_submission()
        self.deployment.status = ExamDeployment.StatusChoices.DEACTIVATED
        self.deployment.save(update_fields=["status"])

        response = self.client.post(
            f"/api/exams/deployments/{self.deployment.id}/cheating/",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 410)
        data = response.json()
        self.assertEqual(data["error_detail"], "시험이 이미 종료되었습니다.")
