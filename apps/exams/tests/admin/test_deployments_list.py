from __future__ import annotations

from datetime import date, timedelta

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam, ExamDeployment, ExamSubmission
from apps.users.models import User


@override_settings(USE_EXAM_MOCK=False)
class AdminExamDeploymentListAPITest(TestCase):
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
            title="Python 시험",
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
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            name="관리자",
            nickname="관리자",
            phone_number="01011112222",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
            role=User.Role.ADMIN,
            is_active=True,
        )
        self.staff_user = User.objects.create_user(
            email="staff@example.com",
            password="password123",
            name="스태프",
            nickname="스태프",
            phone_number="01011112223",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
            role=User.Role.TA,
            is_active=True,
        )
        self.student = User.objects.create_user(
            email="student@example.com",
            password="password123",
            name="학생",
            nickname="학생",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.STUDENT,
            is_active=True,
        )
        ExamSubmission.objects.create(
            submitter=self.student,
            deployment=self.deployment,
            started_at=timezone.now() - timedelta(minutes=10),
            cheating_count=0,
            answers_json=[],
            score=80,
            correct_answer_count=8,
        )

    def _auth_headers(self, user: User) -> dict[str, str]:
        token = AccessToken.for_user(user)
        return {"Authorization": f"Bearer {token}"}

    def test_admin_can_list_deployments(self) -> None:
        response = self.client.get(
            "/api/v1/admin/exams/deployments/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertIn("count", data)
        self.assertGreaterEqual(len(data["results"]), 1)

    def test_staff_can_list_deployments(self) -> None:
        response = self.client.get(
            "/api/v1/admin/exams/deployments/",
            headers=self._auth_headers(self.staff_user),
        )

        self.assertEqual(response.status_code, 200)

    def test_returns_401_when_unauthenticated(self) -> None:
        response = self.client.get("/api/v1/admin/exams/deployments/")

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.UNAUTHORIZED.value)

    def test_returns_403_for_non_staff(self) -> None:
        response = self.client.get(
            "/api/v1/admin/exams/deployments/",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.NO_DEPLOYMENT_LIST_PERMISSION.value)

    def test_filter_by_search_keyword(self) -> None:
        response = self.client.get(
            "/api/v1/admin/exams/deployments/",
            {"search_keyword": "Python"},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["exam"]["title"], "Python 시험")

    def test_filter_by_subject_id(self) -> None:
        other_subject = Subject.objects.create(
            course=self.course,
            title="다른 과목",
            number_of_days=1,
            number_of_hours=1,
            thumbnail_img_url="subject2.png",
        )
        other_exam = Exam.objects.create(subject=other_subject, title="다른 시험", thumbnail_img_url="exam2.png")
        ExamDeployment.objects.create(
            cohort=self.cohort,
            exam=other_exam,
            duration_time=30,
            access_code="CODE2",
            open_at=timezone.now() - timedelta(minutes=5),
            close_at=timezone.now() + timedelta(minutes=30),
            questions_snapshot_json={},
            status=ExamDeployment.StatusChoices.ACTIVATED,
        )

        response = self.client.get(
            "/api/v1/admin/exams/deployments/",
            {"subject_id": self.subject.id},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)

    def test_filter_by_cohort_id(self) -> None:
        other_cohort = Cohort.objects.create(
            course=self.course,
            number=2,
            max_student=10,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )
        ExamDeployment.objects.create(
            cohort=other_cohort,
            exam=self.exam,
            duration_time=30,
            access_code="CODE3",
            open_at=timezone.now() - timedelta(minutes=5),
            close_at=timezone.now() + timedelta(minutes=30),
            questions_snapshot_json={},
            status=ExamDeployment.StatusChoices.ACTIVATED,
        )

        response = self.client.get(
            "/api/v1/admin/exams/deployments/",
            {"cohort_id": self.cohort.id},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)

    def test_returns_400_for_invalid_sort(self) -> None:
        response = self.client.get(
            "/api/v1/admin/exams/deployments/",
            {"sort": "invalid"},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_DEPLOYMENT_LIST_REQUEST.value)
