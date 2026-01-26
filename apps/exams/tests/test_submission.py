from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.courses.models import Cohort, Course, Subject
from apps.exams.models import (
    Exam,
    ExamDeployment,
    ExamQuestion,
    ExamSubmission,
)

User = get_user_model()


class ExamSubmissionTest(APITestCase):
    def setUp(self) -> None:
        self.course = Course.objects.create(
            name="테스트 강좌",
            tag="TST",
        )

        self.subject = Subject.objects.create(
            course=self.course,
            title="테스트 과목",
            number_of_days=5,
            number_of_hours=10,
        )
        self.cohort = Cohort.objects.create(
            course=self.course,
            number=1,
            max_student=30,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )

        self.user = User.objects.create_user(
            email="test@test.com",
            password="1234",
            birthday=date(2000, 1, 1),
            gender=User.Gender.MALE,
            nickname="테스트유저",
            name="테스트 이름",
            phone_number="010-0000-0000",
        )

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # 클라이언트에 Authorization 헤더 설정
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        self.exam = Exam.objects.create(
            title="쪽지시험",
            subject_id=self.subject.id,
        )

        self.question = ExamQuestion.objects.create(
            exam=self.exam,
            question="OX 문제",
            type=ExamQuestion.TypeChoices.OX,
            answer="O",
            point=5,
            explanation="설명",
        )

        self.deployment = ExamDeployment.objects.create(
            exam=self.exam,
            cohort_id=self.cohort.id,
            duration_time=60,
            access_code="ABC123",
            open_at=timezone.now() - timedelta(minutes=5),
            close_at=timezone.now() + timedelta(minutes=5),
            questions_snapshot_json=[
                {
                    "id": self.question.id,
                    "answer": "O",
                    "point": 5,
                    "type": "OX",
                }
            ],
            status=ExamDeployment.StatusChoices.ACTIVATED,
        )

        self.submission = ExamSubmission.objects.create(
            submitter=self.user,
            deployment=self.deployment,
            started_at=self.deployment.open_at,
            answers_json={},
        )

    def test_submission_exam_success(self) -> None:
        response = self.client.post(
            f"/api/v1/exams/submissions",
            {
                "deployment": self.deployment.id,
                "answers": [
                    {
                        "question_id": self.question.id,
                        "submitted_answer": "O",
                        "type": self.question.type,
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["score"], 5)
        self.assertEqual(response.data["correct_answer_count"], 1)
