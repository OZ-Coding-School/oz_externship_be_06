import json

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.constants import ErrorMessages
from apps.qna.models import Answer, Question, QuestionCategory
from apps.qna.tests.factories import create_general_user, create_student_user
from apps.users.models import User


class AnswerCreateAPITest(APITestCase):
    """
    답변 등록 API (POST) 테스트
    - 성공 케이스 (권한 있는 유저)
    - 실패 케이스
        - 401 Unauthorized: 로그인하지 않은 유저
        - 403 Forbidden: 접근 권한이 없는 유저 (일반 유저)
        - 404 Not Found: 존재하지 않는 질문
        - 400 Bad Request: 필수 입력값(내용) 누락
    - 성능 테스트 (쿼리 수 검증)
    """

    student_user: User
    general_user: User
    category: QuestionCategory
    question: Question
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        # 테스트용 유저
        cls.student_user = create_student_user()
        cls.general_user = create_general_user()

        # Base Data
        cls.category = QuestionCategory.objects.create(name="Python")
        cls.question = Question.objects.create(
            author=cls.student_user,
            category=cls.category,
            title="질문입니다",
            content="내용",
        )

        # URL
        cls.url = reverse("answer-create", kwargs={"question_id": cls.question.id})

    # ==========================================================================
    # 성공 케이스
    # ==========================================================================
    def test_create_answer_success(self) -> None:
        """[201] 수강생 계정으로 답변 등록"""
        self.client.force_authenticate(user=self.student_user)

        data: dict[str, object] = {"content": "답변입니다.", "image_urls": ["https://example.com/img1.png"]}

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("answer_id", res_data)
        self.assertEqual(res_data["question_id"], self.question.id)
        self.assertEqual(res_data["author_id"], self.student_user.id)

        # DB Verification
        self.assertTrue(Answer.objects.filter(id=res_data["answer_id"]).exists())

    # ==========================================================================
    # 실패 케이스
    # ==========================================================================
    def test_create_answer_unauthorized(self) -> None:
        """[401] 비로그인 상태로 요청"""
        data = {"content": "답변"}
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.UNAUTHORIZED_ANSWER_CREATE.value)

    def test_create_answer_forbidden(self) -> None:
        """[403] 허용되지 않은 Role(USER)로 요청"""
        self.client.force_authenticate(user=self.general_user)

        data = {"content": "답변"}
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.FORBIDDEN_ANSWER_CREATE.value)

    def test_create_answer_not_found(self) -> None:
        """[404] 존재하지 않는 질문 ID로 요청"""
        self.client.force_authenticate(user=self.student_user)

        invalid_url = reverse("answer-create", kwargs={"question_id": 99999})
        data = {"content": "답변"}
        response = self.client.post(invalid_url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.NOT_FOUND_QUESTION.value)

    def test_create_answer_invalid_input(self) -> None:
        """[400] 필수 필드(content) 누락"""
        self.client.force_authenticate(user=self.student_user)

        data: dict[str, object] = {"image_urls": []}  # content missing
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Serializer's default_error_message is INVALID_ANSWER_CREATE
        self.assertEqual(response.json()["error_detail"], ErrorMessages.INVALID_ANSWER_CREATE.value)

    # ==========================================================================
    # 성능 테스트
    # ==========================================================================
    def test_create_answer_performance(self) -> None:
        """[성능] 답변 등록 시 쿼리 수 검증"""
        self.client.force_authenticate(user=self.student_user)
        data: dict[str, object] = {
            "content": "답변입니다.",
            "image_urls": ["https://example.com/1.png", "https://example.com/2.png"],
        }

        # Query Expectation:
        # 1. Auth check (User) - often cached or 1 query
        # 2. Permission check (Role)
        # 3. Get Question (select_for_update)
        # 4. Create Answer
        # 5. Bulk Create Images
        # 6. Transaction Atomic overhead?

        # Allow roughly 6-8 queries
        with CaptureQueriesContext(connection) as context:
            self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertLessEqual(len(context), 8, f"Too many queries: {len(context)}")
