"""
QnA 예외처리 시나리오별 테스트

테스트 범위:
- CategoryNotFoundException (존재하지 않는 카테고리로 질문 생성)
- ObjectDoesNotExist 중앙 처리 검증
- qna_exception_handler 로깅 검증
- 권한 에러 폴백 메시지 테스트
- 응답 포맷 일관성 검증 ({"error_detail": "..."})
"""

import json
from typing import Any

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions import QnaBaseException
from apps.qna.models import Question, QuestionCategory
from apps.users.models import User


class CategoryNotFoundExceptionTest(TestCase):
    """
    CategoryNotFoundException 테스트
    - 존재하지 않는 카테고리 ID로 질문 생성 시 400 에러 반환 검증
    """

    url: str
    category: QuestionCategory
    student: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = reverse("question-list-create")

        # 유효한 카테고리 생성
        cls.category = QuestionCategory.objects.create(name="ValidCategory")

        # 테스트 유저 (수강생)
        cls.student = User.objects.create_user(
            email="student@test.com",
            password="password123",
            nickname="수강생",
            role="STUDENT",
            birthday="1990-01-01",
            is_active=True,
        )

    def setUp(self) -> None:
        self.client = Client()

    def _get_auth_header(self, user: Any) -> dict[str, Any]:
        refresh = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}

    def test_create_question_with_invalid_category_id(self) -> None:
        """[실패] 존재하지 않는 category_id로 질문 생성 시 400 에러 반환"""
        auth_header = self._get_auth_header(self.student)

        data = {
            "title": "테스트 질문",
            "content": "내용입니다",
            "category_id": 99999,  # 존재하지 않는 ID
        }

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json", **auth_header)
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error_detail", res_data)
        self.assertEqual(res_data["error_detail"], ErrorMessages.NOT_FOUND_CATEGORY.value)

    def test_create_question_with_valid_category_id(self) -> None:
        """[성공] 유효한 category_id로 질문 생성 시 201 반환"""
        auth_header = self._get_auth_header(self.student)

        data = {
            "title": "테스트 질문",
            "content": "내용입니다",
            "category_id": self.category.id,
        }

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json", **auth_header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ExceptionResponseFormatTest(TestCase):
    """
    모든 에러 응답이 {"error_detail": "..."} 포맷을 준수하는지 검증
    """

    category: QuestionCategory
    student: User
    general_user: User
    question: Question

    @classmethod
    def setUpTestData(cls) -> None:
        cls.category = QuestionCategory.objects.create(name="TestCategory")

        cls.student = User.objects.create_user(
            email="student@test.com",
            password="password123",
            nickname="수강생",
            role="STUDENT",
            birthday="1990-01-01",
            is_active=True,
        )

        cls.general_user = User.objects.create_user(
            email="general@test.com",
            password="password123",
            nickname="일반유저",
            role="USER",
            birthday="1995-05-05",
            is_active=True,
        )

        cls.question = Question.objects.create(
            author=cls.student,
            category=cls.category,
            title="테스트 질문",
            content="내용",
        )

    def setUp(self) -> None:
        self.client = Client()

    def _get_auth_header(self, user: Any) -> dict[str, Any]:
        refresh = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}

    def test_401_response_format(self) -> None:
        """[401] 응답 포맷 검증"""
        url = reverse("question-list-create")
        data = {"title": "test", "content": "test", "category_id": self.category.id}

        response = self.client.post(url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        res_data = response.json()
        self.assertIn("error_detail", res_data)
        self.assertEqual(len(res_data.keys()), 1)  # error_detail만 있어야 함

    def test_403_response_format(self) -> None:
        """[403] 응답 포맷 검증"""
        url = reverse("question-list-create")
        auth_header = self._get_auth_header(self.general_user)
        data = {"title": "test", "content": "test", "category_id": self.category.id}

        response = self.client.post(url, data=json.dumps(data), content_type="application/json", **auth_header)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        res_data = response.json()
        self.assertIn("error_detail", res_data)
        self.assertEqual(len(res_data.keys()), 1)

    def test_400_response_format(self) -> None:
        """[400] 응답 포맷 검증 (필수 필드 누락)"""
        url = reverse("question-list-create")
        auth_header = self._get_auth_header(self.student)
        data = {"content": "제목 없음", "category_id": self.category.id}  # title 누락

        response = self.client.post(url, data=json.dumps(data), content_type="application/json", **auth_header)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        res_data = response.json()
        self.assertIn("error_detail", res_data)
        self.assertEqual(len(res_data.keys()), 1)

    def test_404_response_format(self) -> None:
        """[404] 응답 포맷 검증 (존재하지 않는 질문)"""
        url = reverse("question-detail", kwargs={"question_id": 99999})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        res_data = response.json()
        self.assertIn("error_detail", res_data)
        self.assertEqual(len(res_data.keys()), 1)


class ExceptionHandlerLoggingTest(TestCase):
    """
    qna_exception_handler의 로깅 동작 검증
    """

    category: QuestionCategory
    student: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.category = QuestionCategory.objects.create(name="TestCategory")

        cls.student = User.objects.create_user(
            email="student@test.com",
            password="password123",
            nickname="수강생",
            role="STUDENT",
            birthday="1990-01-01",
            is_active=True,
        )

    def setUp(self) -> None:
        self.client = Client()

    def _get_auth_header(self, user: Any) -> dict[str, Any]:
        refresh = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}

    def test_401_error_logging_level(self) -> None:
        """[401] 인증 에러는 INFO 레벨로 로깅되는지 검증"""
        url = reverse("question-list-create")

        with self.assertLogs("apps.qna.exceptions", level="INFO") as log_context:
            self.client.post(
                url,
                data=json.dumps({"title": "t", "content": "c", "category_id": 1}),
                content_type="application/json",
            )

        # INFO 레벨 로그가 있는지 확인
        self.assertTrue(any("[Auth Required]" in msg for msg in log_context.output))

    def test_400_error_logging_level(self) -> None:
        """[400] 클라이언트 에러는 WARNING 레벨로 로깅되는지 검증"""
        url = reverse("question-list-create")
        auth_header = self._get_auth_header(self.student)

        with self.assertLogs("apps.qna.exceptions", level="WARNING") as log_context:
            self.client.post(
                url,
                data=json.dumps({"content": "no title", "category_id": self.category.id}),
                content_type="application/json",
                **auth_header,
            )

        self.assertTrue(any("[Client Error]" in msg for msg in log_context.output))

    def test_404_error_logging_level(self) -> None:
        """[404] Not Found는 INFO 레벨로 로깅되는지 검증"""
        url = reverse("question-detail", kwargs={"question_id": 99999})

        with self.assertLogs("apps.qna.exceptions", level="INFO") as log_context:
            self.client.get(url)

        self.assertTrue(any("[Not Found]" in msg for msg in log_context.output))


class PermissionErrorFallbackTest(TestCase):
    """
    _handle_permission_errors의 폴백 메시지 테스트
    - 매핑되지 않은 View/Method 조합에서도 안전하게 응답
    """

    def test_permission_error_map_question_create(self) -> None:
        """Question POST 매핑 검증"""
        from apps.qna.exceptions.handler import _PERMISSION_ERROR_MAP

        # 401 (인증 에러)
        key_401 = ("QuestionCreateListAPIView", "POST", True)
        self.assertIn(key_401, _PERMISSION_ERROR_MAP)
        self.assertEqual(_PERMISSION_ERROR_MAP[key_401], ErrorMessages.UNAUTHORIZED_QUESTION_CREATE)

        # 403 (권한 에러)
        key_403 = ("QuestionCreateListAPIView", "POST", False)
        self.assertIn(key_403, _PERMISSION_ERROR_MAP)
        self.assertEqual(_PERMISSION_ERROR_MAP[key_403], ErrorMessages.FORBIDDEN_QUESTION_CREATE)

    def test_permission_error_map_answer_create(self) -> None:
        """AnswerCreate POST 매핑 검증"""
        from apps.qna.exceptions.handler import _PERMISSION_ERROR_MAP

        key_401 = ("AnswerCreateAPIView", "POST", True)
        self.assertIn(key_401, _PERMISSION_ERROR_MAP)
        self.assertEqual(_PERMISSION_ERROR_MAP[key_401], ErrorMessages.UNAUTHORIZED_ANSWER_CREATE)

    def test_fallback_message_exists(self) -> None:
        """폴백 메시지 상수 존재 검증"""
        from apps.qna.exceptions.handler import _DEFAULT_AUTH_ERROR, _DEFAULT_PERM_ERROR

        # 폴백 메시지가 ErrorMessages Enum으로 정의되어 있는지 확인
        self.assertIsInstance(_DEFAULT_AUTH_ERROR, ErrorMessages)
        self.assertIsInstance(_DEFAULT_PERM_ERROR, ErrorMessages)
        self.assertEqual(_DEFAULT_AUTH_ERROR, ErrorMessages.DEFAULT_401)
        self.assertEqual(_DEFAULT_PERM_ERROR, ErrorMessages.DEFAULT_403)


class QnaBaseExceptionTest(TestCase):
    """
    QnaBaseException 클래스 직접 테스트
    """

    def test_exception_with_enum_detail(self) -> None:
        """Enum 메시지로 예외 생성 시 value 추출 검증"""
        exc = QnaBaseException(detail=ErrorMessages.INVALID_QUESTION_CREATE)
        self.assertEqual(str(exc.detail), ErrorMessages.INVALID_QUESTION_CREATE.value)

    def test_exception_with_string_detail(self) -> None:
        """문자열 메시지로 예외 생성"""
        exc = QnaBaseException(detail="커스텀 에러 메시지")
        self.assertEqual(str(exc.detail), "커스텀 에러 메시지")

    def test_exception_with_dict_detail(self) -> None:
        """딕셔너리 메시지로 예외 생성 시 error_detail 추출 검증"""
        exc = QnaBaseException(detail={"error_detail": "딕셔너리 에러"})
        self.assertEqual(str(exc.detail), "딕셔너리 에러")

    def test_exception_default_detail(self) -> None:
        """기본 메시지 사용 검증"""
        exc = QnaBaseException()
        self.assertEqual(str(exc.detail), ErrorMessages.DEFAULT_400.value)
