from typing import Any
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import date

from apps.exams.models import Exam, ExamQuestion
from apps.courses.models import Subject, Course
from apps.exams.constants import ErrorMessages
from apps.exams.services.admin.questions_update import update_exam_question, BusinessRuleError
from apps.exams.exceptions import ErrorDetailException

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
        self.assertIn(
            ErrorMessages.UNAUTHORIZED.value,
            str(response.data),
        )

    # 3. 권한 없음 (403)
    def test_update_question_forbidden(self) -> None:
        self.client.force_authenticate(self.user)

        payload = {"point": 5}

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error_detail"],
            ErrorMessages.NO_QUESTION_UPDATE_PERMISSION.value,
        )

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

        # 기존 문제들 총점 95로 세팅
        ExamQuestion.objects.create(
            exam=self.exam,
            type=ExamQuestion.TypeChoices.SHORT_ANSWER,
            question="dummy 1",
            prompt="",
            options_json=None,
            blank_count=0,
            answer="dummy answer",
            point=50,
            explanation="",
        )
        ExamQuestion.objects.create(
            exam=self.exam,
            type=ExamQuestion.TypeChoices.SHORT_ANSWER,
            question="dummy 2",
            prompt="",
            options_json=None,
            blank_count=0,
            answer="dummy answer",
            point=45,
            explanation="",
        )

        payload = {
            "point": 10,
            "correct_answer": ["A", "B"],
            "options": ["A", "B"],
        }

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.data["error_detail"],
            ErrorMessages.QUESTION_UPDATE_CONFLICT.value,
        )

    # 7. 타입 변경 + 필수 필드 누락 (400)
    # correct_answer 누락
    def test_update_question_change_type_missing_required_fields(self) -> None:
        self.client.force_authenticate(self.admin)

        payload = {
            "type": ExamQuestion.TypeChoices.SHORT_ANSWER,
            "question": "단답형으로 변경",
            "point": 5,
        }

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    # 8. ORDERING + 보기 1개 (최소 개수 위반) (400)
    def test_update_question_ordering_with_single_option(self) -> None:
        self.client.force_authenticate(self.admin)

        payload = {
            "type": ExamQuestion.TypeChoices.ORDERING,
            "options": ["A"],  # 최소 2개 위반
            "correct_answer": ["A"],
            "point": 5,
        }

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    # 9. OX 타입 변경 성공 (200)
    def test_update_question_change_type_to_ox_success(self) -> None:
        self.client.force_authenticate(self.admin)

        payload = {
            "type": ExamQuestion.TypeChoices.OX,
            "question": "OX 문제로 변경",
            "correct_answer": True,
            "point": 5,
        }

        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["type"], ExamQuestion.TypeChoices.OX)
        self.assertEqual(response.data["point"], 5)

    # service에 대한 엣지 케이스
    # payload가 비었을 때
    def test_service_empty_payload_raises_error(self) -> None:
        question = self.question
        update_data: dict[str, Any] = {}

        with self.assertRaises(ErrorDetailException):
            update_exam_question(instance=question, update_data=update_data)

    # 필수 필드 누락
    def test_service_type_change_missing_required_fields(self) -> None:
        question = self.question
        update_data = {"type": ExamQuestion.TypeChoices.SHORT_ANSWER, "question": "단답형으로 변경"}

        with self.assertRaises(BusinessRuleError):
            update_exam_question(instance=question, update_data=update_data)