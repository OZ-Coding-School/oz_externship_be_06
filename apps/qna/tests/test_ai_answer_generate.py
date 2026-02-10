from typing import Any
from unittest.mock import patch

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.constants import ErrorMessages
from apps.qna.models import Question, QuestionAIAnswer, QuestionCategory
from apps.users.models import User


class AIAnswerGenerateAPITest(APITestCase):
    """
    AI 답변 생성 API (GET) 테스트
    - 성공 케이스: 로그인한 유저가 AI 답변 생성 성공
    - 실패 케이스
        - 401 Unauthorized: 비로그인 유저
        - 404 Not Found: 존재하지 않는 질문
        - 409 Conflict: 이미 AI 답변이 존재하는 경우
    - 성능 테스트 (쿼리 수 검증)
    """

    student: User
    category: QuestionCategory
    question: Question
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        # 테스트용 유저 - 학생
        cls.student = User.objects.create_user(
            email="student@ozcoding.com",
            password="password123",
            name="테스트학생",
            nickname="학생",
            role="STUDENT",
            birthday="2000-01-01",
            is_active=True,
        )
        # 테스트용 카테고리 및 질문 생성
        cls.category = QuestionCategory.objects.create(name="Python")
        cls.question = Question.objects.create(
            author=cls.student,
            category=cls.category,
            title="리스트와 튜플의 차이점",
            content="파이썬에서 리스트와 튜플의 차이점이 무엇인가요?",
        )

        # URL
        cls.url = reverse("ai-answer-generate", kwargs={"question_id": cls.question.id})


    @patch("apps.qna.services.answer.command.AIAnswerCommandService._call_ai_model")
    def test_generate_ai_answer_success(self, mock_call_ai: Any) -> None:
        """[성공] 로그인한 유저가 AI 답변 생성 성공 검증"""
        # AI API 모킹
        mock_call_ai.return_value = "리스트는 수정 가능한 자료구조이며, 튜플은 수정이 불가능한 자료구조입니다."

        self.client.force_authenticate(user=self.student)

        response = self.client.get(self.url)
        res_data = response.json()

        # 응답 검증
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res_data)
        self.assertEqual(res_data["question_id"], self.question.id)
        self.assertIn("output", res_data)
        self.assertIn("using_model", res_data)
        self.assertIn("created_at", res_data)

        # DB 검증
        self.assertTrue(QuestionAIAnswer.objects.filter(question=self.question).exists())

        # 질문 상태 업데이트 검증
        self.question.refresh_from_db()
        self.assertTrue(self.question.is_ai_answered)

    def test_generate_ai_answer_unauthorized(self) -> None:
        """[실패] 비로그인 유저 요청 시 401 반환 검증"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_generate_ai_answer_not_found(self) -> None:
        """[실패] 존재하지 않는 질문 ID로 요청 시 404 반환 검증"""
        self.client.force_authenticate(user=self.student)

        invalid_url = reverse("ai-answer-generate", kwargs={"question_id": 99999})
        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.NOT_FOUND_AI_QUESTION.value)

    @patch("apps.qna.services.answer.command.AIAnswerCommandService._call_ai_model")
    def test_generate_ai_answer_conflict(self, mock_call_ai: Any) -> None:
        """[실패] 이미 AI 답변이 존재하는 경우 409 반환 검증"""
        # 기존 AI 답변 생성
        QuestionAIAnswer.objects.create(
            question=self.question,
            output="기존 AI 답변입니다.",
            using_model="Gemini",
        )

        self.client.force_authenticate(user=self.student)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.ALREADY_EXISTS_AI_ANSWER.value)

        # AI API가 호출되지 않았는지 검증
        mock_call_ai.assert_not_called()

    @patch("apps.qna.services.answer.command.AIAnswerCommandService._call_ai_model")
    def test_generate_ai_answer_response_format(self, mock_call_ai: Any) -> None:
        """[성공] 응답 데이터 형식 검증"""
        mock_call_ai.return_value = "테스트 AI 답변입니다."

        self.client.force_authenticate(user=self.student)

        response = self.client.get(self.url)
        res_data = response.json()

        # 응답 필드 검증
        self.assertIsInstance(res_data["id"], int)
        self.assertIsInstance(res_data["question_id"], int)
        self.assertIsInstance(res_data["output"], str)
        self.assertIsInstance(res_data["using_model"], str)
        self.assertIsInstance(res_data["created_at"], str)

        # using_model 값 검증 (Gemini 또는 GPT)
        self.assertIn(res_data["using_model"], ["Gemini", "GPT"])

    @patch("apps.qna.services.answer.command.AIAnswerCommandService._call_ai_model")
    def test_generate_ai_answer_performance(self, mock_call_ai: Any) -> None:
        """[성공] AI 답변 생성 시 쿼리 수 검증"""
        mock_call_ai.return_value = "성능 테스트용 AI 답변"

        self.client.force_authenticate(user=self.student)

        # Query Expectation:
        # 1. Auth check (User)
        # 2. Get Question
        # 3. Check existing AI Answer
        # 4. Create AI Answer
        # 5. Update Question (is_ai_answered)

        with CaptureQueriesContext(connection) as context:
            self.client.get(self.url)

        # Allow roughly 6-8 queries
        self.assertLessEqual(len(context), 8, f"Too many queries: {len(context)}")
