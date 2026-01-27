from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.courses.models import Cohort, CohortStudent, Course
from apps.users.models import User


class AdminCourseCreateAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/admin/courses/"

        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="관리자",
            nickname="admin",
            gender="MALE",
            role=User.Role.ADMIN,
        )

        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345679",
            name="수강생",
            nickname="student",
            gender="MALE",
            role=User.Role.STUDENT,
        )

    def _set_auth(self, user: User) -> None:
        access = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_create_course_success_201(self) -> None:
        self._set_auth(self.admin_user)

        data = {
            "name": "새로운 과정",
            "tag": "NEW",
            "description": "새로운 과정 설명",
            "thumbnail_img_url": "https://example.com/image.png",
        }

        res = self.client.post(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        response_data = res.json()
        self.assertEqual(response_data["detail"], "과정이 등록되었습니다.")
        self.assertIn("id", response_data)

        course = Course.objects.get(id=response_data["id"])
        self.assertEqual(course.name, "새로운 과정")
        self.assertEqual(course.tag, "NEW")

    def test_create_course_without_optional_fields_201(self) -> None:
        self._set_auth(self.admin_user)

        data = {
            "name": "필수만 있는 과정",
            "tag": "REQ",
        }

        res = self.client.post(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_course_invalid_data_400(self) -> None:
        self._set_auth(self.admin_user)

        data = {
            "name": "",
            "tag": "TOOLONG",
        }

        res = self.client.post(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_course_unauthenticated_401(self) -> None:
        data = {"name": "과정", "tag": "TAG"}

        res = self.client.post(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_course_forbidden_403(self) -> None:
        self._set_auth(self.student_user)

        data = {"name": "과정", "tag": "TAG"}

        res = self.client.post(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCourseUpdateAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()

        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="관리자",
            nickname="admin",
            gender="MALE",
            role=User.Role.ADMIN,
        )

        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345679",
            name="수강생",
            nickname="student",
            gender="MALE",
            role=User.Role.STUDENT,
        )

        self.course = Course.objects.create(
            name="기존 과정",
            tag="OLD",
            description="기존 설명",
        )

        self.url = f"/api/v1/admin/courses/{self.course.id}/"

    def _set_auth(self, user: User) -> None:
        access = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_update_course_success_200(self) -> None:
        self._set_auth(self.admin_user)

        data = {
            "name": "수정된 과정",
            "tag": "MOD",
        }

        res = self.client.patch(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        response_data = res.json()
        self.assertEqual(response_data["name"], "수정된 과정")
        self.assertEqual(response_data["tag"], "MOD")

        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "수정된 과정")
        self.assertEqual(self.course.tag, "MOD")

    def test_update_course_partial_200(self) -> None:
        self._set_auth(self.admin_user)

        data = {"description": "수정된 설명만"}

        res = self.client.patch(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.description, "수정된 설명만")
        self.assertEqual(self.course.name, "기존 과정")

    def test_update_course_not_found_404(self) -> None:
        self._set_auth(self.admin_user)

        url = "/api/v1/admin/courses/99999/"
        data = {"name": "없는 과정"}

        res = self.client.patch(url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error_detail", res.json())

    def test_update_course_unauthenticated_401(self) -> None:
        data = {"name": "수정"}

        res = self.client.patch(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_course_forbidden_403(self) -> None:
        self._set_auth(self.student_user)

        data = {"name": "수정"}

        res = self.client.patch(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCourseDeleteAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()

        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="관리자",
            nickname="admin",
            gender="MALE",
            role=User.Role.ADMIN,
        )

        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345679",
            name="수강생",
            nickname="student",
            gender="MALE",
            role=User.Role.STUDENT,
        )

        self.course = Course.objects.create(
            name="삭제할 과정",
            tag="DEL",
        )

        self.url = f"/api/v1/admin/courses/{self.course.id}/"

    def _set_auth(self, user: User) -> None:
        access = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_delete_course_success_204(self) -> None:
        self._set_auth(self.admin_user)

        res = self.client.delete(self.url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())

    def test_delete_course_with_cohort_cascade_204(self) -> None:
        self._set_auth(self.admin_user)

        cohort = Cohort.objects.create(
            course=self.course,
            number=1,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
            status=Cohort.StatusChoices.PREPARING,
        )

        res = self.client.delete(self.url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())
        self.assertFalse(Cohort.objects.filter(id=cohort.id).exists())

    def test_delete_course_with_students_400(self) -> None:
        self._set_auth(self.admin_user)

        cohort = Cohort.objects.create(
            course=self.course,
            number=1,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
            status=Cohort.StatusChoices.IN_PROGRESS,
        )

        CohortStudent.objects.create(user=self.student_user, cohort=cohort)

        res = self.client.delete(self.url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", res.json())
        self.assertTrue(Course.objects.filter(id=self.course.id).exists())

    def test_delete_course_not_found_404(self) -> None:
        self._set_auth(self.admin_user)

        url = "/api/v1/admin/courses/99999/"

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error_detail", res.json())

    def test_delete_course_unauthenticated_401(self) -> None:
        res = self.client.delete(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_course_forbidden_403(self) -> None:
        self._set_auth(self.student_user)

        res = self.client.delete(self.url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
