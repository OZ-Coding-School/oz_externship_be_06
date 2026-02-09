from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.courses.models import Cohort, Course, Subject
from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import Exam, ExamDeployment, ExamSubmission
from apps.users.models import User


class AdminExamDeploymentDeleteAPITest(TestCase):
    staff_user: User
    normal_user: User
    course: Course
    cohort: Cohort
    subject: Subject
    exam: Exam
    deployment: ExamDeployment
    submission: ExamSubmission

    @classmethod
    def setUpTestData(cls) -> None:
        cls.staff_user = User.objects.create_user(
            email="staff@example.com",
            password="password",
            role=User.Role.ADMIN,
            name="Staff Name",
            nickname="Staff",
            phone_number="01012345678",
            gender="MALE",
            birthday=date(1990, 1, 1),
        )

        cls.normal_user = User.objects.create_user(
            email="user@example.com",
            password="password",
            is_staff=False,
            name="User Name",
            nickname="User",
            phone_number="01011111111",
            gender="MALE",
            birthday=date(1980, 11, 18),
        )

        cls.course = Course.objects.create(
            name="Python Course",
            tag="PY",  # 3글자 이하
            description="Python 기초 강좌",
            thumbnail_img_url=None,
        )

        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            start_date=date(2026, 2, 5),
            end_date=date(2026, 5, 5),
        )

        cls.subject = Subject.objects.create(
            course=cls.course,
            title="Python 기초",
            number_of_days=30,
            number_of_hours=60,
            status=True,
        )

        cls.exam = Exam.objects.create(
            subject=cls.subject,
            title="Python 기초 시험",
            thumbnail_img_url="default_img_url",
        )

        cls.deployment = ExamDeployment.objects.create(
            cohort=cls.cohort,
            exam=cls.exam,
            access_code="ABC123",
            open_at=timezone.now(),
            close_at=timezone.now() + timedelta(hours=1),
            questions_snapshot_json=[],
        )

        cls.submission = ExamSubmission.objects.create(
            deployment=cls.deployment,
            submitter=cls.staff_user,
            started_at=cls.deployment.open_at,
            answers_json={"q1": "a"},
        )

    def setUp(self) -> None:
        self.client: APIClient = APIClient()

    def test_success_delete_deployment(self) -> None:
        self.client.force_authenticate(user=self.staff_user)

        url = reverse(
            "admin-exam-deployment-detail",
            kwargs={"deployment_id": self.deployment.id},
        )

        # delete 요청
        response = self.client.delete(url)

        # 응답 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["deployment_id"], self.deployment.id)
        self.assertFalse(ExamDeployment.objects.filter(id=self.deployment.id).exists())
        self.assertFalse(ExamSubmission.objects.filter(deployment=self.deployment).exists())

    def test_400_when_invalid_deployment_id(self) -> None:
        self.client.force_authenticate(user=self.staff_user)

        url = reverse(
            "admin-exam-deployment-detail",
            kwargs={"deployment_id": 0},
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_401_when_not_authenticated(self) -> None:
        url = reverse("admin-exam-deployment-detail", kwargs={"deployment_id": self.deployment.id})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_403_when_not_staff(self) -> None:
        self.client.force_authenticate(user=self.normal_user)

        url = reverse(
            "admin-exam-deployment-detail",
            kwargs={"deployment_id": self.deployment.id},
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_404_when_deployment_not_found(self) -> None:
        self.client.force_authenticate(user=self.staff_user)
        url = reverse("admin-exam-deployment-detail", kwargs={"deployment_id": 999999})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # View에서 사용 중인 delete_exam_deployment 참조를 mock
    @patch("apps.exams.views.admin.deployments_detail.delete_exam_deployment")
    def test_409_on_conflict(self, mock_delete: MagicMock) -> None:
        mock_delete.side_effect = ErrorDetailException(
            ErrorMessages.DEPLOYMENT_DELETE_CONFLICT.value,
            status.HTTP_409_CONFLICT,
        )

        self.client.force_authenticate(user=self.staff_user)
        url = reverse("admin-exam-deployment-detail", kwargs={"deployment_id": self.deployment.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.data["error_detail"],
            ErrorMessages.DEPLOYMENT_DELETE_CONFLICT.value,
        )
