from __future__ import annotations

from datetime import date
from typing import Any, Dict, cast

from django.test import Client, TestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam
from apps.users.models import User


class AdminExamDetailAPITest(TestCase):
    course: Course
    subject: Subject
    exam: Exam
    admin_user: User
    normal_user: User
    url: str

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
        self.exam = Exam.objects.create(
            subject=self.subject,
            title="시험1",
            thumbnail_img_url="exam.png",
        )

        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            name="어드민",
            nickname="어드민닉",
            phone_number="01099999999",
            gender=User.Gender.MALE,
            birthday=date(1995, 1, 1),
            role=User.Role.ADMIN,
            is_active=True,
        )

        self.normal_user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            name="일반유저",
            nickname="닉네임",
            phone_number="01011111111",
            gender=User.Gender.FEMALE,
            birthday=date(2000, 1, 1),
            role=User.Role.USER,
            is_active=True,
        )

        self.url = f"/api/v1/admin/exams/{self.exam.id}"

    def _auth_client(self, user: User) -> Client:
        token: AccessToken = AccessToken.for_user(user)
        client: Client = Client()
        client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        return client

    def test_401_when_no_auth(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

        data = cast(Dict[str, Any], response.json())
        self.assertEqual(
            data["error_detail"],
            ErrorMessages.UNAUTHORIZED.value,
        )

    def test_403_when_not_admin(self) -> None:
        client = self._auth_client(self.normal_user)

        response = client.get(self.url)

        self.assertEqual(response.status_code, 403)

        data = cast(Dict[str, Any], response.json())
        self.assertEqual(
            data["error_detail"],
            ErrorMessages.NO_EXAM_LIST_PERMISSION.value,
        )

    def test_400_when_invalid_exam_id(self) -> None:
        client = self._auth_client(self.admin_user)

        response = client.get("/api/v1/admin/exams/0")

        self.assertEqual(response.status_code, 400)

        data = cast(Dict[str, Any], response.json())
        self.assertEqual(
            data["error_detail"],
            ErrorMessages.INVALID_EXAM_LIST_REQUEST.value,
        )

    def test_404_when_exam_not_found(self) -> None:
        client = self._auth_client(self.admin_user)

        response = client.get("/api/v1/admin/exams/99999999")

        self.assertEqual(response.status_code, 404)

        data = cast(Dict[str, Any], response.json())
        self.assertEqual(
            data["error_detail"],
            ErrorMessages.EXAM_NOT_FOUND.value,
        )

    def test_200_success(self) -> None:
        client = self._auth_client(self.admin_user)

        response = client.get(self.url)

        self.assertEqual(response.status_code, 200)

        data = cast(Dict[str, Any], response.json())

        # 키 존재 확인
        self.assertIn("id", data)
        self.assertIn("title", data)
        self.assertIn("subject", data)
        self.assertIn("questions", data)
        self.assertIn("thumbnail_img_url", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

        self.assertEqual(data["id"], self.exam.id)
        self.assertEqual(data["title"], self.exam.title)

        subject_data = cast(Dict[str, Any], data["subject"])
        self.assertEqual(subject_data["id"], self.subject.id)
        self.assertEqual(subject_data["title"], self.subject.title)
