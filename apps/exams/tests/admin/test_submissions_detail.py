from datetime import date, datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam, ExamDeployment, ExamSubmission
from apps.users.models import User


class AdminExamSubmissionDetailAPITest(TestCase):
    """어드민 쪽지시험 응시 내역 상세 조회 API 테스트."""

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
        self.deployment = ExamDeployment.objects.create(
            exam=self.exam,
            cohort=self.cohort,
            duration_time=45,
            access_code="ACCESSCODE",
            open_at=timezone.make_aware(datetime(2025, 3, 2, 10, 0, 0)),
            close_at=timezone.make_aware(datetime(2025, 3, 2, 12, 0, 0)),
            questions_snapshot_json=[
                {
                    "question_id": 1,
                    "type": "MULTIPLE_CHOICE",
                    "question": "다음 중 Python의 특징은?",
                    "prompt": None,
                    "options": ["인터프리터", "정적 타입"],
                    "point": 10,
                    "answer": "인터프리터",
                    "explanation": "설명",
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
            is_active=True,
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
            is_active=True,
        )
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="password123",
            name="수강생",
            nickname="수강생",
            phone_number="01011114444",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 3),
            role=User.Role.STUDENT,
            is_active=True,
        )
        started_at = timezone.now() - timedelta(minutes=30)
        self.submission = ExamSubmission.objects.create(
            submitter=self.student_user,
            deployment=self.deployment,
            started_at=started_at,
            cheating_count=1,
            answers_json=[{"question_id": 1, "submitted_answer": "인터프리터"}],
            score=10,
            correct_answer_count=1,
        )
        self.expected_elapsed = int((self.submission.created_at - started_at).total_seconds() // 60)

    def _auth_headers(self, user: User) -> dict[str, str]:
        token = AccessToken.for_user(user)
        return {"Authorization": f"Bearer {token}"}

    def test_admin_can_get_submission_detail(self) -> None:
        response = self.client.get(
            f"/api/v1/admin/exams/submissions/{self.submission.id}/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["exam"]["exam_title"], "시험")
        self.assertEqual(data["exam"]["subject_name"], "과목")
        self.assertEqual(data["student"]["course_name"], self.course.name)
        self.assertEqual(data["student"]["cohort_number"], self.cohort.number)
        self.assertEqual(data["result"]["score"], 10)
        self.assertEqual(data["result"]["correct_answer_count"], 1)
        self.assertEqual(data["result"]["total_question_count"], 1)
        self.assertEqual(data["result"]["cheating_count"], 1)
        self.assertEqual(data["result"]["elapsed_time"], self.expected_elapsed)
        self.assertEqual(data["questions"][0]["type"], "multiple_choice")
        self.assertTrue(data["questions"][0]["is_correct"])

    def test_returns_400_when_invalid_submission_id(self) -> None:
        response = self.client.get(
            "/api/v1/admin/exams/submissions/0/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_SUBMISSION_DETAIL_REQUEST.value)

    def test_returns_401_when_unauthenticated(self) -> None:
        response = self.client.get(f"/api/v1/admin/exams/submissions/{self.submission.id}/")

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.UNAUTHORIZED.value)

    def test_returns_403_for_non_staff(self) -> None:
        response = self.client.get(
            f"/api/v1/admin/exams/submissions/{self.submission.id}/",
            headers=self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.NO_SUBMISSION_DETAIL_PERMISSION.value)

    def test_returns_404_when_submission_missing(self) -> None:
        response = self.client.get(
            "/api/v1/admin/exams/submissions/9999/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.SUBMISSION_DETAIL_NOT_FOUND.value)
