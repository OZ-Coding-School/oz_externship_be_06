from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.models import Exam, ExamDeployment, ExamQuestion, ExamSubmission
from apps.users.models import User


class ExamResultRetrieveAPITest(TestCase):
    def setUp(self) -> None:
        self.course = Course.objects.create(name="코스", tag="CS", description="설명", thumbnail_img_url="course.png")
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
        self.deployment = ExamDeployment.objects.create(
            cohort=self.cohort,
            exam=self.exam,
            duration_time=30,
            access_code="CODE",
            open_at=timezone.now() - timedelta(minutes=30),
            close_at=timezone.now() + timedelta(minutes=30),
            questions_snapshot_json={},
            status=ExamDeployment.StatusChoices.ACTIVATED,
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
            is_active=True,
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="password123",
            name="다른유저",
            nickname="다른유저",
            phone_number="01000000000",
            gender=User.Gender.FEMALE,
            birthday=date(2000, 1, 2),
            role=User.Role.STUDENT,
            is_active=True,
        )

        self.q1 = ExamQuestion.objects.create(
            exam=self.exam,
            question="객관식 문제",
            type=ExamQuestion.TypeChoices.MULTI_SELECT,
            answer="A",
            point=5,
            options_json="{invalid-json",
            explanation="설명",
        )
        self.q2 = ExamQuestion.objects.create(
            exam=self.exam,
            question="빈칸 문제",
            type=ExamQuestion.TypeChoices.FILL_IN_BLANK,
            answer=["a", "b"],
            point=10,
            options_json='["a","b","c"]',
            explanation="설명",
        )

        self.submission = ExamSubmission.objects.create(
            submitter=self.student,
            deployment=self.deployment,
            started_at=timezone.now() - timedelta(minutes=10),
            cheating_count=0,
            answers_json=[],
        )

        self.url = f"/api/v1/exams/submissions/{self.submission.id}"

    def _bearer(self, user: User) -> str:
        token = AccessToken.for_user(user)
        return f"Bearer {token}"

    def test_result_retrieve_success(self) -> None:
        self.submission.answers_json = [
            "invalid",
            {"question_id": None, "submitted_answer": "A"},
            {"question_id": "bad", "submitted_answer": "A"},
            {"question_id": self.q1.id, "submitted_answer": "A"},
            {"question_id": self.q2.id, "submitted_answer": ["a", "b"]},
        ]
        self.submission.save(update_fields=["answers_json"])

        res = self.client.get(self.url, HTTP_AUTHORIZATION=self._bearer(self.student))
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.assertEqual(data.get("id"), self.submission.id)
        self.submission.refresh_from_db()
        self.assertIsInstance(self.submission.answers_json, list)
        self.assertGreaterEqual(len(self.submission.answers_json), 2)

    def test_result_requires_authentication(self) -> None:
        res = self.client.get(self.url)
        self.assertIn(res.status_code, [401, 403])

    def test_result_returns_403_for_other_user(self) -> None:
        res = self.client.get(self.url, HTTP_AUTHORIZATION=self._bearer(self.other_user))
        self.assertEqual(res.status_code, 403)

    def test_result_returns_404_for_missing_submission(self) -> None:
        url = "/api/v1/exams/submissions/999999"
        res = self.client.get(url, HTTP_AUTHORIZATION=self._bearer(self.student))
        self.assertEqual(res.status_code, 404)

    def test_result_returns_400_for_invalid_session(self) -> None:
        self.submission.answers_json = {}
        self.submission.save(update_fields=["answers_json"])
        res = self.client.get(self.url, HTTP_AUTHORIZATION=self._bearer(self.student))
        self.assertEqual(res.status_code, 400)
