from __future__ import annotations

import tempfile
from io import BytesIO
from typing import Any, ClassVar

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from PIL import Image
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models.exams import Exam
from apps.users.models import User


class AdminExamCreateAPITest(TestCase):
    """관리자 쪽지시험 생성 API 테스트."""

    _temp_media: ClassVar[tempfile.TemporaryDirectory[str]]
    _override: ClassVar[Any]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls._temp_media = tempfile.TemporaryDirectory()
        cls._override = override_settings(MEDIA_ROOT=cls._temp_media.name, MEDIA_URL="media/")
        cls._override.enable()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._override.disable()
        cls._temp_media.cleanup()
        super().tearDownClass()

    def setUp(self) -> None:
        self.client = Client()
        self.course = Course.objects.create(name="Python", tag="PY")
        self.subject = Subject.objects.create(
            course=self.course,
            title="Python Basic",
            number_of_days=10,
            number_of_hours=40,
        )
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="password1234",
            name="Admin",
            nickname="admin",
            phone_number="01000000000",
            gender=User.Gender.MALE,
            birthday="2000-01-01",
            role=User.Role.ADMIN,
        )
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            password="password1234",
            name="User",
            nickname="user",
            phone_number="01000000001",
            gender=User.Gender.MALE,
            birthday="2000-01-01",
            role=User.Role.USER,
        )

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def _auth_client(self, user: User) -> Client:
        client = Client()
        client.defaults.update(self._auth_headers(user))
        return client

    def _create_image_file(self) -> SimpleUploadedFile:
        image = Image.new("RGB", (1, 1), color="white")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return SimpleUploadedFile(
            name="thumbnail.png",
            content=buffer.getvalue(),
            content_type="image/png",
        )

    def test_admin_exam_create_success(self) -> None:
        image_file = self._create_image_file()
        data = {
            "title": "Python Basic Exam",
            "subject_id": self.subject.id,
            "thumbnail_img": image_file,
        }

        response = self._auth_client(self.admin_user).post(
            "/api/v1/admin/exams",
            data=data,
        )

        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(response_data["title"], data["title"])
        self.assertEqual(response_data["subject_id"], self.subject.id)
        self.assertIn("media/", response_data["thumbnail_img_url"])
        self.assertTrue(Exam.objects.filter(id=response_data["id"]).exists())

    def test_admin_exam_create_returns_401_when_unauthenticated(self) -> None:
        response = self.client.post(
            "/api/v1/admin/exams",
            data={"title": "Python Basic Exam", "subject_id": self.subject.id},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], ErrorMessages.UNAUTHORIZED.value)

    def test_admin_exam_create_returns_403_when_not_staff(self) -> None:
        image_file = self._create_image_file()
        response = self._auth_client(self.normal_user).post(
            "/api/v1/admin/exams",
            data={
                "title": "Python Basic Exam",
                "subject_id": self.subject.id,
                "thumbnail_img": image_file,
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], ErrorMessages.NO_EXAM_CREATE_PERMISSION.value)

    def test_admin_exam_create_returns_404_when_subject_missing(self) -> None:
        image_file = self._create_image_file()
        response = self._auth_client(self.admin_user).post(
            "/api/v1/admin/exams",
            data={
                "title": "Python Basic Exam",
                "subject_id": 9999,
                "thumbnail_img": image_file,
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.SUBJECT_NOT_FOUND.value)

    def test_admin_exam_create_returns_409_when_duplicate_title(self) -> None:
        Exam.objects.create(subject=self.subject, title="Python Basic Exam", thumbnail_img_url="media/test.png")
        image_file = self._create_image_file()

        response = self._auth_client(self.admin_user).post(
            "/api/v1/admin/exams",
            data={
                "title": "Python Basic Exam",
                "subject_id": self.subject.id,
                "thumbnail_img": image_file,
            },
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.EXAM_CONFLICT.value)

    def test_admin_exam_create_returns_400_when_invalid(self) -> None:
        response = self._auth_client(self.admin_user).post(
            "/api/v1/admin/exams",
            data={"title": "", "subject_id": self.subject.id},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.INVALID_EXAM_CREATE_REQUEST.value)

    def test_admin_exam_create_returns_400_when_invalid_image_type(self) -> None:
        image_file = SimpleUploadedFile(
            name="thumbnail.gif",
            content=b"GIF89a",
            content_type="image/gif",
        )

        response = self._auth_client(self.admin_user).post(
            "/api/v1/admin/exams",
            data={
                "title": "Python Basic Exam",
                "subject_id": self.subject.id,
                "thumbnail_img": image_file,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.INVALID_EXAM_CREATE_REQUEST.value)
