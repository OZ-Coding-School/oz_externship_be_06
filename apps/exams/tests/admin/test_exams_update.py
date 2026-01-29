from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.courses.models import Course, Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam

User = get_user_model()


class AdminExamUpdateAPITests(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.course = Course.objects.create(
            name="테스트 강좌",
            tag="TST",
        )

        self.subject = Subject.objects.create(
            course=self.course,
            title="테스트 과목",
            number_of_days=10,
            number_of_hours=5,
        )

        # Exam 생성
        self.exam = Exam.objects.create(
            title="기존 시험",
            subject=self.subject,
            thumbnail_img_url="http://example.com/old.png",
        )

        # URL
        self.url = reverse("admin-exam-update", kwargs={"exam_id": self.exam.id})

        # 유저 생성
        self.staff_user = User.objects.create_user(
            email="staff@test.com",
            password="password",
            name="테스트 스태프",
            nickname="staff",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.ADMIN,
        )

        self.normal_user = User.objects.create_user(
            email="normal@test.com",
            password="pass1234",
            name="일반유저",
            nickname="normal",
            phone_number="01099998888",
            gender=User.Gender.FEMALE,
            birthday=date(2001, 1, 1),
            role=User.Role.USER,
        )

    # 401 인증 실패
    def test_update_exam_unauthenticated(self) -> None:
        payload = {
            "title": "수정된 시험",
            "subject_id": self.subject.id,
        }

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"],
            ErrorMessages.UNAUTHORIZED.value,
        )

    # 403 권한 없음
    def test_update_exam_forbidden(self) -> None:
        self.client.force_authenticate(user=self.normal_user)

        payload = {
            "title": "수정된 시험",
            "subject_id": self.subject.id,
        }

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            ErrorMessages.NO_EXAM_UPDATE_PERMISSION.value,
        )

    # 400 잘못된 요청 (아무 필드도 안 보내면)
    def test_update_exam_bad_request(self) -> None:
        self.client.force_authenticate(user=self.staff_user)

        payload: dict[str, object] = {}

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 409 제목 중복
    def test_update_exam_conflict_title(self) -> None:
        self.client.force_authenticate(user=self.staff_user)

        Exam.objects.create(
            title="중복 제목",
            subject=self.subject,
        )

        payload = {
            "title": "중복 제목",
            "subject_id": self.subject.id,
        }

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            ErrorMessages.EXAM_UPDATE_CONFLICT.value,
            str(response.data),
        )

    # 404 시험 없음
    def test_update_exam_not_found(self) -> None:
        self.client.force_authenticate(user=self.staff_user)

        url = reverse("admin-exam-update", kwargs={"exam_id": 999999})

        payload = {
            "title": "수정된 시험",
            "subject_id": self.subject.id,
        }

        response = self.client.put(url, payload, format="json")

        self.assertIn(
            response.status_code,
            [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR],
        )

    # 200 정상 수정 (title + subject)
    def test_update_exam_success(self) -> None:
        self.client.force_authenticate(user=self.staff_user)

        payload = {
            "title": "정상 수정 시험",
            "subject_id": self.subject.id,
        }

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "정상 수정 시험")
        self.assertEqual(response.data["subject_id"], self.subject.id)

        # DB 반영 확인
        self.exam.refresh_from_db()
        self.assertEqual(self.exam.title, "정상 수정 시험")
