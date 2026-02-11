import json

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions.base import QnaBaseException
from apps.qna.models import Question, QuestionCategory
from apps.qna.tests.factories import create_general_user, create_student_user
from apps.users.models import User


class QuestionCreateAPITest(APITestCase):
    """
    질문 등록 API (POST) 테스트
    - 성공 케이스 (권한 있는 유저)
    - 실패 케이스
        - 401 Unauthorized: 로그인하지 않은 유저
        - 403 Forbidden: 수강생이 아닌 유저
        - 400 Bad Request: 필수 입력값(제목 등) 누락
    - 성능 테스트 (쿼리 수 검증)
    """

    student_user: User
    general_user: User
    category: QuestionCategory
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        # 테스트용 유저
        cls.student_user = create_student_user()
        cls.general_user = create_general_user()

        # 테스트용 카테고리 생성
        cls.category = QuestionCategory.objects.create(name="OZ_category")

        # URL
        cls.url = reverse("questions")

    # ==========================================================================
    # 성공 케이스
    # ==========================================================================
    def test_create_question_success(self) -> None:
        """[201] 수강생 권한으로 유효한 데이터로 질문 등록"""
        self.client.force_authenticate(user=self.student_user)

        data = {
            "title": "장고 질문입니다.",
            "content": "이 에러는 어떻게 해결하나요?",
            "category_id": self.category.id,
        }

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_data["message"], "질문이 성공적으로 등록되었습니다.")
        self.assertIn("question_id", res_data)
        self.assertTrue(Question.objects.filter(id=res_data["question_id"]).exists())

    # ==========================================================================
    # 실패 케이스
    # ==========================================================================
    def test_create_question_unauthorized(self) -> None:
        """[401] 로그인하지 않은 경우"""
        data = {"title": "비회원 질문", "content": "내용", "category_id": self.category.id}

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.UNAUTHORIZED_QUESTION_CREATE.value)

    def test_create_question_forbidden(self) -> None:
        """[403] 수강생이 아닌 유저 요청"""
        self.client.force_authenticate(user=self.general_user)

        data = {"title": "일반인 질문", "content": "내용", "category_id": self.category.id}

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.FORBIDDEN_QUESTION_CREATE.value)

    def test_create_question_bad_request(self) -> None:
        """[400] 필수 데이터 누락"""
        self.client.force_authenticate(user=self.student_user)

        # 필수 필드인 title 누락
        data = {"content": "제목이 없어요", "category_id": self.category.id}

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")
        res_data = response.json()

        self.assertEqual(response.status_code, QnaBaseException.status_code)
        self.assertEqual(res_data["error_detail"], ErrorMessages.INVALID_QUESTION_CREATE.value)

    # ==========================================================================
    # 성능 테스트
    # ==========================================================================
    def test_create_question_performance(self) -> None:
        """[성능] 질문 등록 시 쿼리 수 검증"""

        self.client.force_authenticate(user=self.student_user)
        data = {
            "title": "성능 테스트 질문",
            "content": "내용",
            "category_id": self.category.id,
        }

        # Query Expectation:
        # 1. Auth check (User)
        # 2. Permission check (Role)
        # 3. Create Question
        # 4. Atomic transaction overhead / signals?
        # 5. Get Category validation
        # 6. Response serialization (if necessary)

        # Allow roughly 6 queries
        with CaptureQueriesContext(connection) as context:
            self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertLessEqual(len(context), 6, f"Expected 6 or fewer queries, but got {len(context)}")
