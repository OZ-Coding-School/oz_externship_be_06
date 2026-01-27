import json
from datetime import date, datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.models import Exam, ExamDeployment, ExamQuestion
from apps.users.models import User


class AdminExamDeploymentCreateAPITest(TestCase):
    """어드민 쪽지시험 배포 생성 API 테스트."""

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
        )

    def _auth_headers(self, user: User) -> dict[str, str]:
        token = AccessToken.for_user(user)
        return {"Authorization": f"Bearer {token}"}

    def test_admin_can_create_deployment(self) -> None:
        payload = {
            "exam_id": self.exam.id,
            "cohort_id": self.cohort.id,
            "duration_time": 45,
            "open_at": "2025-03-02 10:00:00",
            "close_at": "2025-03-02 12:00:00",
        }

        response = self.client.post(
            "/api/v1/admin/exams/deployments/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        deployment = ExamDeployment.objects.get(id=data["pk"])
        self.assertEqual(deployment.exam_id, self.exam.id)
        self.assertEqual(deployment.cohort_id, self.cohort.id)
        self.assertEqual(deployment.duration_time, 45)
        self.assertTrue(deployment.access_code)
        self.assertIsInstance(deployment.questions_snapshot_json, list)

    def test_returns_401_when_unauthenticated(self) -> None:
        payload = {
            "exam_id": self.exam.id,
            "cohort_id": self.cohort.id,
            "duration_time": 45,
            "open_at": "2025-03-02 10:00:00",
            "close_at": "2025-03-02 12:00:00",
        }

        response = self.client.post(
            "/api/v1/admin/exams/deployments/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_returns_403_for_non_staff(self) -> None:
        payload = {
            "exam_id": self.exam.id,
            "cohort_id": self.cohort.id,
            "duration_time": 45,
            "open_at": "2025-03-02 10:00:00",
            "close_at": "2025-03-02 12:00:00",
        }

        response = self.client.post(
            "/api/v1/admin/exams/deployments/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data["detail"], "쪽지시험 관리 권한이 없습니다.")

    def test_returns_404_when_exam_missing(self) -> None:
        payload = {
            "exam_id": 9999,
            "cohort_id": self.cohort.id,
            "duration_time": 45,
            "open_at": "2025-03-02 10:00:00",
            "close_at": "2025-03-02 12:00:00",
        }

        response = self.client.post(
            "/api/v1/admin/exams/deployments/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error_detail"], "배포 대상 과정-기수 또는 시험 정보를 찾을 수 없습니다.")

    def test_returns_404_when_cohort_missing(self) -> None:
        payload = {
            "exam_id": self.exam.id,
            "cohort_id": 9999,
            "duration_time": 45,
            "open_at": "2025-03-02 10:00:00",
            "close_at": "2025-03-02 12:00:00",
        }

        response = self.client.post(
            "/api/v1/admin/exams/deployments/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error_detail"], "배포 대상 과정-기수 또는 시험 정보를 찾을 수 없습니다.")

    def test_returns_409_when_duplicate_deployment(self) -> None:
        open_at = timezone.make_aware(datetime(2025, 3, 2, 10, 0, 0))
        close_at = timezone.make_aware(datetime(2025, 3, 2, 12, 0, 0))
        ExamDeployment.objects.create(
            exam=self.exam,
            cohort=self.cohort,
            duration_time=45,
            access_code="CODE",
            open_at=open_at,
            close_at=close_at,
            questions_snapshot_json=[],
        )
        payload = {
            "exam_id": self.exam.id,
            "cohort_id": self.cohort.id,
            "duration_time": 45,
            "open_at": "2025-03-02 10:00:00",
            "close_at": "2025-03-02 12:00:00",
        }

        response = self.client.post(
            "/api/v1/admin/exams/deployments/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertEqual(data["error_detail"], "동일한 조건의 배포가 이미 존재합니다.")

    def test_returns_400_when_invalid_payload(self) -> None:
        payload = {
            "exam_id": self.exam.id,
            "cohort_id": self.cohort.id,
            "duration_time": 0,
            "open_at": "2025-03-02 12:00:00",
            "close_at": "2025-03-02 10:00:00",
        }

        response = self.client.post(
            "/api/v1/admin/exams/deployments/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], "유효하지 않은 배포 생성 요청입니다.")
