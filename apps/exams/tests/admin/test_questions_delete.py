from datetime import date, timedelta
from typing import Any

from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam, ExamQuestion
from apps.users.models import User


class AdminExamQuestionDeleteAPITest(TestCase):
    """어드민 쪽지시험 문제 삭제 API 테스트."""

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
        self.question = ExamQuestion.objects.create(
            exam=self.exam,
            question="OX 문제",
            type=ExamQuestion.TypeChoices.OX,
            answer="O",
            point=5,
            explanation="",
        )
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            name="관리자",
            nickname="관리자",
            phone_number="01011112222",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.ADMIN,
            is_active=True,
        )
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            name="사용자",
            nickname="사용자",
            phone_number="01011113333",
            gender=User.Gender.FEMALE,
            birthday=date(2000, 1, 2),
            role=User.Role.USER,
            is_active=True,
        )

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"Authorization": f"Bearer {token}"}

    def test_admin_can_delete_question(self) -> None:
        response = self.client.delete(
            f"/api/v1/admin/exams/questions/{self.question.id}/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["exam_id"], self.exam.id)
        self.assertEqual(data["question_id"], self.question.id)
        self.assertFalse(ExamQuestion.objects.filter(id=self.question.id).exists())

    def test_returns_401_when_unauthenticated(self) -> None:
        response = self.client.delete(f"/api/v1/admin/exams/questions/{self.question.id}/")

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["detail"], ErrorMessages.UNAUTHORIZED.value)

    def test_returns_403_for_non_staff(self) -> None:
        response = self.client.delete(
            f"/api/v1/admin/exams/questions/{self.question.id}/",
            headers=self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data["detail"], ErrorMessages.NO_QUESTION_DELETE_PERMISSION.value)

    def test_returns_404_when_question_missing(self) -> None:
        response = self.client.delete(
            "/api/v1/admin/exams/questions/9999/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.QUESTION_NOT_FOUND.value)

    def test_returns_400_when_invalid_ids(self) -> None:
        response = self.client.delete(
            "/api/v1/admin/exams/questions/0/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_QUESTION_DELETE_REQUEST.value)
