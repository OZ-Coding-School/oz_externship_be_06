from datetime import date, datetime, timedelta

from django.test import TestCase
from django.utils import timezone

from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.models import Exam, ExamDeployment, ExamQuestion, ExamSubmission
from apps.exams.tasks import auto_submit_overdue_exams
from apps.users.models import User


class AutoSubmitOverdueExamsTaskTest(TestCase):
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

        ExamQuestion.objects.create(
            exam=self.exam,
            question="문제",
            type=ExamQuestion.TypeChoices.SINGLE_CHOICE,
            answer="A",
            point=5,
            options_json='["A","B"]',
            explanation="설명",
        )

    def _create_submission(self, *, started_at: datetime, duration_minutes: int) -> ExamSubmission:
        deployment = ExamDeployment.objects.create(
            cohort=self.cohort,
            exam=self.exam,
            duration_time=duration_minutes,
            access_code="CODE",
            open_at=timezone.now() - timedelta(minutes=30),
            close_at=timezone.now() + timedelta(minutes=30),
            questions_snapshot_json={},
            status=ExamDeployment.StatusChoices.ACTIVATED,
        )
        return ExamSubmission.objects.create(
            submitter=self.student,
            deployment=deployment,
            started_at=started_at,
            cheating_count=0,
            answers_json={},
        )

    def test_auto_submit_overdue_submission(self) -> None:
        now = timezone.now()
        submission = self._create_submission(
            started_at=now - timedelta(minutes=10),
            duration_minutes=1,
        )

        processed = auto_submit_overdue_exams()

        self.assertEqual(processed, 1)
        submission.refresh_from_db()
        self.assertIsInstance(submission.answers_json, list)
        self.assertGreaterEqual(len(submission.answers_json), 1)

    def test_does_not_submit_if_not_overdue(self) -> None:
        now = timezone.now()
        submission = self._create_submission(
            started_at=now - timedelta(minutes=1),
            duration_minutes=30,
        )

        processed = auto_submit_overdue_exams()

        self.assertEqual(processed, 0)
        submission.refresh_from_db()
        self.assertEqual(submission.answers_json, {})
