from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import date

from apps.exams.models import Exam, ExamQuestion
from apps.courses.models import Subject, Course

User = get_user_model()


class AdminExamQuestionUpdateAPITests(APITestCase):
    def setUp(self) -> None:
        # 관리자 유저
        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="password",
            birthday=date(1990, 1, 1),
            role=User.Role.ADMIN,
        )

        # 일반 유저
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            birthday=date(1995, 5, 5),
            is_staff=False,
        )

        # 수강
        self.course = Course.objects.create(
            name="테스트 강좌",
            tag="T01",
            description="테스트 강좌 설명",
        )

        # 과목
        self.subject = Subject.objects.create(
            course=self.course,
            title="테스트 과목",
            number_of_days=30,
            number_of_hours=10,
            status=True,
        )

        # 시험
        self.exam = Exam.objects.create(title="테스트 시험", subject=self.subject)

        # 기존 문제
        self.question = ExamQuestion.objects.create(
            exam=self.exam,
            type=ExamQuestion.TypeChoices.ORDERING,
            question="기존 문제",
            prompt="",
            options_json='["A", "B"]',
            blank_count=0,
            answer=["A", "B"],
            point=5,
            explanation="기존 해설",
        )

        self.url = reverse(
            "admin-exam-question-update",
            kwargs={"question_id": self.question.id},
        )

    # 1. 성공 (200)
    def test_update_question_success(self) -> None:
        self.client.force_authenticate(self.admin)

        payload = {
            "question": "수정된 문제",
            "point": 7,
            "options": ["A", "B", "C"],
            "correct_answer": ["A", "B", "C"],
            "explanation": "수정된 해설",
        }

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["question"], "수정된 문제")
        self.assertEqual(response.data["point"], 7)
        self.assertEqual(response.data["options"], ["A", "B", "C"])
        self.assertEqual(response.data["explanation"], "수정된 해설")

    # 2. 인증 안됨 (401)
    def test_update_question_unauthenticated(self) -> None:
        payload = {"point": 5}

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error_detail", response.data)

    # 3. 권한 없음 (403)
    def test_update_question_forbidden(self) -> None:
        self.client.force_authenticate(self.user)

        payload = {"point": 5}

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error_detail", response.data)

    # 4. 시험 문제 없음 (404)
    def test_update_question_not_found(self) -> None:
        self.client.force_authenticate(self.admin)

        url = reverse(
            "admin-exam-question-update",
            kwargs={"question_id": 999999}
        )

        response = self.client.put(url, {"point": 5}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error_detail", response.data)

    # 5. 비즈니스 룰 위반 (400)
    # ORDERING인데 options 비움
    def test_update_question_business_rule_error(self) -> None:
        self.client.force_authenticate(self.admin)

        payload = {
            "type": ExamQuestion.TypeChoices.ORDERING,
            "options": [],
        }

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    # 6. 총점 초과 (409)
    def test_update_question_conflict_total_score(self) -> None:
        self.client.force_authenticate(self.admin)

        payload = {"point": 200}

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("error_detail", response.data)
