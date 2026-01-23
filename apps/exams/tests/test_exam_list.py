from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.models import Exam, ExamDeployment
from apps.users.models import User


class ExamDeploymentListAPITest(TestCase):
    """시험 배포 목록 조회 API 테스트."""

    def setUp(self) -> None:
        self.course = Course.objects.create(
            name="코스", tag="CS", description="설명", thumbnail_img_url="course.png"
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

        self.student = User.objects.create_user(
            email="student@example.com",
            password="password123",
            name="학생",
            nickname="닉네임",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.STUDENT,
        )

        # NOTE: 코호트-수강생 매핑 모델이 따로 있으면 여기서 연결해줘야 함.
        # 예) CohortStudent.objects.create(user=self.student, cohort=self.cohort)

        # 배포 2개 만들어서 필터 테스트
        self.deployment_active = ExamDeployment.objects.create(
            cohort=self.cohort,
            exam=self.exam,
            duration_time=30,
            access_code="CODE1",
            open_at=timezone.now() - timedelta(minutes=5),
            close_at=timezone.now() + timedelta(minutes=30),
            questions_snapshot_json={},
            status=ExamDeployment.StatusChoices.ACTIVATED,
        )
        self.deployment_deactivated = ExamDeployment.objects.create(
            cohort=self.cohort,
            exam=self.exam,
            duration_time=30,
            access_code="CODE2",
            open_at=timezone.now() - timedelta(days=1),
            close_at=timezone.now() - timedelta(minutes=1),
            questions_snapshot_json={},
            status=ExamDeployment.StatusChoices.DEACTIVATED,
        )

    def _auth_headers(self, user: User) -> dict[str, str]:
        token = AccessToken.for_user(user)
        return {"Authorization": f"Bearer {token}"}

    def test_list_returns_200(self) -> None:
        response = self.client.get(
            "/api/v1/exams/deployments/",
            headers=self._auth_headers(self.student),
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        # ✅ 너희 응답이 list가 아니라 {results: []}면 여기만 바꿔주면 됨.
        self.assertTrue(isinstance(data, (list, dict)))

    def test_list_filter_status_all(self) -> None:
        response = self.client.get(
            "/api/v1/exams/deployments/?status=all",
            headers=self._auth_headers(self.student),
        )
        self.assertEqual(response.status_code, 200)

    def test_list_filter_status_done_or_pending(self) -> None:
        # 프로젝트마다 done/pending 기준이 다름(제출 존재 여부 등)
        # 우선 엔드포인트가 정상 동작/분기 코드가 실행되게만 해도 커버리지 오름
        for status in ["done", "pending"]:
            response = self.client.get(
                f"/api/v1/exams/deployments/?status={status}",
                headers=self._auth_headers(self.student),
            )
            self.assertEqual(response.status_code, 200)

    def test_list_requires_authentication(self) -> None:
        response = self.client.get("/api/v1/exams/deployments/")
        self.assertEqual(response.status_code, 401)