from __future__ import annotations

import json
from typing import Any

from django.test import Client, TestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models.exams import Exam
from apps.users.models import User


class AdminExamCreateAPITest(TestCase):
    """관리자 쪽지시험 생성 API 테스트."""

    course: Course
    subject: Subject
    admin_user: User
    normal_user: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.course = Course.objects.create(name="Python", tag="PY")
        cls.subject = Subject.objects.create(
            course=cls.course,
            title="Python Basic",
            number_of_days=10,
            number_of_hours=40,
        )
        cls.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="password1234",
            name="Admin",
            nickname="admin",
            phone_number="01000000000",
            gender=User.Gender.MALE,
            birthday="2000-01-01",
            role=User.Role.ADMIN,
            is_active=True,
        )
        cls.normal_user = User.objects.create_user(
            email="user@example.com",
            password="password1234",
            name="User",
            nickname="user",
            phone_number="01000000001",
            gender=User.Gender.MALE,
            birthday="2000-01-01",
            role=User.Role.USER,
            is_active=True,
        )

    def setUp(self) -> None:
        self.client = Client()

    def _auth_headers(self, user: User) -> dict[str, str]:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def _auth_client(self, user: User) -> Client:
        client = Client()
        client.defaults.update(self._auth_headers(user))
        return client

    def _post_json(self, client: Client, url: str, payload: dict[str, object]) -> Any:
        return client.post(url, data=json.dumps(payload), content_type="application/json")

    def test_admin_exam_create_success(self) -> None:
        data = {
            "title": "Python Basic Exam",
            "subject_id": self.subject.id,
            "thumbnail_img_url": "https://cdn.example.com/exams/thumb.png",
        }

        response = self._post_json(self._auth_client(self.admin_user), "/api/v1/admin/exams", data)

        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(response_data["title"], data["title"])
        self.assertEqual(response_data["subject_id"], self.subject.id)
        self.assertEqual(response_data["thumbnail_img_url"], data["thumbnail_img_url"])
        self.assertTrue(Exam.objects.filter(id=response_data["id"]).exists())

    def test_admin_exam_create_without_thumbnail(self) -> None:
        response = self._post_json(
            self._auth_client(self.admin_user),
            "/api/v1/admin/exams",
            {
                "title": "Python Basic Exam No Image",
                "subject_id": self.subject.id,
            },
        )

        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(response_data["title"], "Python Basic Exam No Image")
        self.assertEqual(response_data["subject_id"], self.subject.id)
        self.assertTrue(Exam.objects.filter(id=response_data["id"]).exists())

    def test_admin_exam_create_returns_401_when_unauthenticated(self) -> None:
        response = self._post_json(
            self.client,
            "/api/v1/admin/exams",
            {"title": "Python Basic Exam", "subject_id": self.subject.id},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.UNAUTHORIZED.value)

    def test_admin_exam_create_returns_403_when_not_staff(self) -> None:
        response = self._post_json(
            self._auth_client(self.normal_user),
            "/api/v1/admin/exams",
            {
                "title": "Python Basic Exam",
                "subject_id": self.subject.id,
                "thumbnail_img_url": "https://cdn.example.com/exams/thumb.png",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.NO_EXAM_CREATE_PERMISSION.value)

    def test_admin_exam_create_returns_404_when_subject_missing(self) -> None:
        response = self._post_json(
            self._auth_client(self.admin_user),
            "/api/v1/admin/exams",
            {
                "title": "Python Basic Exam",
                "subject_id": 9999,
                "thumbnail_img_url": "https://cdn.example.com/exams/thumb.png",
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.SUBJECT_NOT_FOUND.value)

    def test_admin_exam_create_returns_409_when_duplicate_title(self) -> None:
        Exam.objects.create(subject=self.subject, title="Python Basic Exam", thumbnail_img_url="media/test.png")

        response = self._post_json(
            self._auth_client(self.admin_user),
            "/api/v1/admin/exams",
            {
                "title": "Python Basic Exam",
                "subject_id": self.subject.id,
                "thumbnail_img_url": "https://cdn.example.com/exams/thumb.png",
            },
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.EXAM_CONFLICT.value)

    def test_admin_exam_create_returns_400_when_invalid(self) -> None:
        response = self._post_json(
            self._auth_client(self.admin_user),
            "/api/v1/admin/exams",
            {"title": "", "subject_id": self.subject.id},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.INVALID_EXAM_CREATE_REQUEST.value)
