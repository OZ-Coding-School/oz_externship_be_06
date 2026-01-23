from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.models import Exam, ExamDeployment, ExamSubmission
from apps.users.models import User


class ExamResultRetrieveAPITest(TestCase):
    """시험 제출 결과 상세 조회 API 테스트."""

    def setUp(self) -> None:
        self.course = Course.objects.create(
            name="코스", tag="CS", description="설명", thumbnail_img_url="course.png"
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
            open_at=timezone.now() - timedelta(minutes=30),
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

        self.submission = ExamSubmission.objects.create(
            submitter=self.student,
            deployment=self.deployment,
            started_at=timezone.now() - timedelta(minutes=10),
            created_at=timezone.now(),
            score=80,  # 필드 없으면 제거/수정
            correct_answer_count=8,  # 필드 없으면 제거/수정
            cheating_count=0,
            answers_json=[],
        )

    def _auth_headers(self, user: User) -> dict[str, str]:
        token = AccessToken.for_user(user)
        return {"Authorization": f"Bearer {token}"}

    def test_result_retrieve_success(self) -> None:
        # ⚠️ 너희 URL이 /submissions/{id}/ 이런 형태면 여기만 바꿔줘
        response = self.client.get(
            f"/api/v1/exams/submissions/{self.submission.id}/",
            headers=self._auth_headers(self.student),
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        # 아래 키는 너희 serializer 필드명대로 맞춰
        self.assertEqual(data["id"], self.submission.id)

    def test_result_requires_authentication(self) -> None:
        response = self.client.get(f"/api/v1/exams/submissions/{self.submission.id}/")
        self.assertEqual(response.status_code, 401)

    def test_result_returns_404_when_missing(self) -> None:
        response = self.client.get(
            "/api/v1/exams/submissions/999999/",
            headers=self._auth_headers(self.student),
        )
        self.assertEqual(response.status_code, 404)