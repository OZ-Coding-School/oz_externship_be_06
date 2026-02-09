from datetime import date, datetime, timedelta

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam, ExamDeployment, ExamQuestion
from apps.users.models import User


@override_settings(USE_EXAM_MOCK=False)
class AdminExamDeploymentUpdateAPITest(TestCase):
    """어드민 쪽지시험 배포 수정 API 테스트."""

    course: Course
    subject: Subject
    cohort: Cohort
    exam: Exam
    question: ExamQuestion
    deployment: ExamDeployment
    admin_user: User
    normal_user: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.course = Course.objects.create(
            name="코스",
            tag="CS",
            description="설명",
            thumbnail_img_url="course.png",
        )
        cls.subject = Subject.objects.create(
            course=cls.course,
            title="과목",
            number_of_days=1,
            number_of_hours=1,
            thumbnail_img_url="subject.png",
        )
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=11,
            max_student=30,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )
        cls.exam = Exam.objects.create(
            subject=cls.subject,
            title="시험",
            thumbnail_img_url="exam.png",
        )
        cls.question = ExamQuestion.objects.create(
            exam=cls.exam,
            question="OX 문제",
            type=ExamQuestion.TypeChoices.OX,
            answer="O",
            point=5,
            explanation="",
        )
        cls.deployment = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort,
            duration_time=45,
            access_code="ACCESSCODE",
            open_at=timezone.make_aware(datetime(2025, 3, 2, 10, 0, 0)),
            close_at=timezone.make_aware(datetime(2025, 3, 2, 12, 0, 0)),
            questions_snapshot_json=[
                {
                    "question_id": cls.question.id,
                    "type": cls.question.type,
                    "question": cls.question.question,
                    "prompt": cls.question.prompt,
                    "blank_count": cls.question.blank_count,
                    "options": None,
                    "point": cls.question.point,
                }
            ],
        )
        cls.admin_user = User.objects.create_user(
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
        cls.normal_user = User.objects.create_user(
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

    def _auth_headers(self, user: User) -> dict[str, str]:
        token = AccessToken.for_user(user)
        return {"Authorization": f"Bearer {token}"}

    def test_admin_can_update_deployment(self) -> None:
        payload = {
            "open_at": "2025-03-02 10:30:00",
            "close_at": "2025-03-02 12:30:00",
            "duration_time": 50,
        }
        response = self.client.patch(
            f"/api/v1/admin/exams/deployments/{self.deployment.id}",
            data=payload,
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["deployment_id"], self.deployment.id)
        self.assertEqual(data["duration_time"], 50)
        self.assertEqual(data["open_at"], "2025-03-02 10:30:00")
        self.assertEqual(data["close_at"], "2025-03-02 12:30:00")
        self.assertIn("updated_at", data)

        self.deployment.refresh_from_db()
        self.assertEqual(self.deployment.duration_time, 50)
        self.assertEqual(
            self.deployment.open_at,
            timezone.make_aware(datetime(2025, 3, 2, 10, 30, 0)),
        )
        self.assertEqual(
            self.deployment.close_at,
            timezone.make_aware(datetime(2025, 3, 2, 12, 30, 0)),
        )

    def test_returns_400_when_duration_exceeds_window(self) -> None:
        """시험 시간이 배포 구간(open_at~close_at)보다 길면 400."""
        payload = {
            "open_at": "2025-03-02 10:00:00",
            "close_at": "2025-03-02 11:00:00",  # 1시간 = 60분
            "duration_time": 90,  # 90분 > 60분
        }
        response = self.client.patch(
            f"/api/v1/admin/exams/deployments/{self.deployment.id}",
            data=payload,
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_DEPLOYMENT_UPDATE_REQUEST.value)

    def test_returns_400_when_invalid_deployment_id(self) -> None:
        response = self.client.patch(
            "/api/v1/admin/exams/deployments/0",
            data={"open_at": "2025-03-02 10:00:00", "close_at": "2025-03-02 12:00:00", "duration_time": 45},
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_DEPLOYMENT_UPDATE_REQUEST.value)

    def test_returns_401_when_unauthenticated(self) -> None:
        response = self.client.patch(
            f"/api/v1/admin/exams/deployments/{self.deployment.id}",
            data={"open_at": "2025-03-02 10:00:00", "close_at": "2025-03-02 12:00:00", "duration_time": 45},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.UNAUTHORIZED.value)

    def test_returns_403_for_non_staff(self) -> None:
        response = self.client.patch(
            f"/api/v1/admin/exams/deployments/{self.deployment.id}",
            data={"open_at": "2025-03-02 10:00:00", "close_at": "2025-03-02 12:00:00", "duration_time": 45},
            content_type="application/json",
            headers=self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.NO_DEPLOYMENT_UPDATE_PERMISSION.value)

    def test_returns_404_when_deployment_missing(self) -> None:
        response = self.client.patch(
            "/api/v1/admin/exams/deployments/9999",
            data={"open_at": "2025-03-02 10:00:00", "close_at": "2025-03-02 12:00:00", "duration_time": 45},
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.DEPLOYMENT_UPDATE_NOT_FOUND.value)
