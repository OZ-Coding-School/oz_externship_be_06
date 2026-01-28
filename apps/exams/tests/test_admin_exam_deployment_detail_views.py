from datetime import date, datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohort_students import CohortStudent
from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.models import Exam, ExamDeployment, ExamQuestion, ExamSubmission
from apps.exams.constants import ErrorMessages
from apps.users.models import User


class AdminExamDeploymentDetailAPITest(TestCase):
    """어드민 쪽지시험 배포 상세 조회 API 테스트."""

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
            number=11,
            max_student=30,
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
        self.deployment = ExamDeployment.objects.create(
            exam=self.exam,
            cohort=self.cohort,
            duration_time=45,
            access_code="ACCESSCODE",
            open_at=timezone.make_aware(datetime(2025, 3, 2, 10, 0, 0)),
            close_at=timezone.make_aware(datetime(2025, 3, 2, 12, 0, 0)),
            questions_snapshot_json=[
                {
                    "question_id": self.question.id,
                    "type": self.question.type,
                    "question": self.question.question,
                    "prompt": self.question.prompt,
                    "blank_count": self.question.blank_count,
                    "options": None,
                    "point": self.question.point,
                }
            ],
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
        self.student1 = User.objects.create_user(
            email="student1@example.com",
            password="password123",
            name="수강생1",
            nickname="수강생1",
            phone_number="01011114444",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 3),
            role=User.Role.STUDENT,
        )
        self.student2 = User.objects.create_user(
            email="student2@example.com",
            password="password123",
            name="수강생2",
            nickname="수강생2",
            phone_number="01011115555",
            gender=User.Gender.FEMALE,
            birthday=date(2000, 1, 4),
            role=User.Role.STUDENT,
        )
        self.student3 = User.objects.create_user(
            email="student3@example.com",
            password="password123",
            name="수강생3",
            nickname="수강생3",
            phone_number="01011116666",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 5),
            role=User.Role.STUDENT,
        )
        CohortStudent.objects.create(user=self.student1, cohort=self.cohort)
        CohortStudent.objects.create(user=self.student2, cohort=self.cohort)
        CohortStudent.objects.create(user=self.student3, cohort=self.cohort)
        ExamSubmission.objects.create(
            submitter=self.student1,
            deployment=self.deployment,
            started_at=timezone.now(),
            cheating_count=0,
            answers_json={},
            score=0,
            correct_answer_count=0,
        )

    def _auth_headers(self, user: User) -> dict[str, str]:
        token = AccessToken.for_user(user)
        return {"Authorization": f"Bearer {token}"}

    def test_admin_can_get_deployment_detail(self) -> None:
        response = self.client.get(
            f"/api/v1/admin/exams/deployments/{self.deployment.id}/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.deployment.id)
        self.assertEqual(data["access_code"], "ACCESSCODE")
        self.assertEqual(data["submit_count"], 1)
        self.assertEqual(data["not_submitted_count"], 2)
        self.assertEqual(data["exam"]["id"], self.exam.id)
        self.assertEqual(data["subject"]["id"], self.subject.id)
        self.assertEqual(
            data["exam_access_url"],
            f"http://testserver/api/v1/exams/deployments/{self.deployment.id}",
        )

    def test_returns_400_when_invalid_deployment_id(self) -> None:
        response = self.client.get(
            "/api/v1/admin/exams/deployments/0/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_DEPLOYMENT_DETAIL_REQUEST.value)

    def test_returns_401_when_unauthenticated(self) -> None:
        response = self.client.get(f"/api/v1/admin/exams/deployments/{self.deployment.id}/")

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_returns_403_for_non_staff(self) -> None:
        response = self.client.get(
            f"/api/v1/admin/exams/deployments/{self.deployment.id}/",
            headers=self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data["detail"], "쪽지시험 관리 권한이 없습니다.")

    def test_returns_404_when_deployment_missing(self) -> None:
        response = self.client.get(
            "/api/v1/admin/exams/deployments/9999/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.DEPLOYMENT_NOT_FOUND.value)
