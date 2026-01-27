from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


class CourseListAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/course/"

        User = get_user_model()
        self.user = User.objects.create_user(
            email="course_list_test@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="테스터",
            nickname="tester",
            gender="MALE",
        )

        access = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_course_list_success_200(self) -> None:
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)

        self.assertEqual(data[0]["id"], 1)
        self.assertEqual(data[0]["name"], "초격차 백엔드 부트캠프")
        self.assertEqual(data[0]["tag"], "BE")

        self.assertEqual(data[1]["id"], 2)
        self.assertEqual(data[1]["name"], "초격차 프론트엔드 부트캠프")
        self.assertEqual(data[1]["tag"], "FE")

        self.assertEqual(data[2]["id"], 3)
        self.assertEqual(data[2]["name"], "풀스택 개발자 과정")
        self.assertEqual(data[2]["tag"], "FS")

    def test_course_list_unauthenticated_401(self) -> None:
        self.client.credentials()

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
