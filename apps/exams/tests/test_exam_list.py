from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohort_students import CohortStudent  # ✅ 실제 경로
from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.models import Exam, ExamDeployment
from apps.users.models import User


class ExamDeploymentListAPITest(TestCase):

    def setUp(self) -> None:
        self.course = Course.objects.create(name="코스", tag="CS", description="설명", thumbnail_img_url="course.png")
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

        CohortStudent.objects.create(user=self.student, cohort=self.cohort)  # type: ignore[attr-defined]

        ExamDeployment.objects.create(
            cohort=self.cohort,
            exam=self.exam,
            duration_time=30,
            access_code="CODE1",
            open_at=timezone.now() - timedelta(minutes=5),
            close_at=timezone.now() + timedelta(minutes=30),
            questions_snapshot_json={},
            status=ExamDeployment.StatusChoices.ACTIVATED,
        )

        self.url = "/api/v1/exams/deployments"  # 끝 슬래시 X

    def _bearer(self, user: User) -> str:
        token = AccessToken.for_user(user)
        return f"Bearer {token}"

    def test_list_returns_200(self) -> None:
        res = self.client.get(self.url, HTTP_AUTHORIZATION=self._bearer(self.student))
        self.assertEqual(res.status_code, 200)

    def test_list_requires_authentication(self) -> None:
        res = self.client.get(self.url)
        # 프로젝트에 따라 401/403 중 하나일 수 있어서 안전하게 처리
        self.assertIn(res.status_code, [401, 403])
