from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.exams.models import Exam, ExamQuestion

User = get_user_model()


class AdminExamQuestionUpdateAPITests(APITestCase):
    def setUp(self):
        # 관리자 유저
        self.admin = User.objects.create_user(
            username="admin",
            password="pass",
            is_staff=True,
        )

        # 일반 유저
        self.user = User.objects.create_user(
            username="user",
            password="pass",
            is_staff=False,
        )

        # 시험
        self.exam = Exam.objects.create(title="테스트 시험")

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
    def test_update_question_success(self):
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
    def test_update_question_unauthenticated(self):
        payload = {"point": 5}

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error_detail", response.data)

    # 3. 권한 없음 (403)
    def test_update_question_forbidden(self):
        self.client.force_authenticate(self.user)

        payload = {"point": 5}

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error_detail", response.data)

    # 4. 시험 문제 없음 (404)
    def test_update_question_not_found(self):
        self.client.force_authenticate(self.admin)

        url = "/api/v1/admin/exams/questions/999999"

        response = self.client.put(url, {"point": 5}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error_detail", response.data)

    # 5. 비즈니스 룰 위반 (400)
    # ORDERING인데 options 비움
    def test_update_question_business_rule_error(self):
        self.client.force_authenticate(self.admin)

        payload = {
            "type": ExamQuestion.TypeChoices.ORDERING,
            "options": [],
        }

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    # 6. 총점 초과 (409)
    def test_update_question_conflict_total_score(self):
        self.client.force_authenticate(self.admin)

        payload = {"point": 200}

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("error_detail", response.data)
