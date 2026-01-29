import json
from typing import Any

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import Client, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.qna.exceptions.question_exception import QuestionBaseException
from apps.qna.models import Question, QuestionCategory

User = get_user_model()


@override_settings(USE_QNA_MOCK=False)
class QuestionCreateAPITest(TestCase):
    """
    질문 등록 API (POST) 테스트
    - 등록 성공 검증
    - 400, 401, 403 에러 매핑 검증
    """

    def setUp(self) -> None:
        # Django 내장 TestClient 초기화
        self.client = Client()

        # 테스트용 카테고리 생성
        self.category = QuestionCategory.objects.create(name="OZ_category")

        # 테스트용 유저 생성 (수강생)
        self.student_user = User.objects.create_user(
            email="student@ozcoding.com",
            password="password123",
            name="test1",
            nickname="수강생",
            role="STUDENT",
            gender="MAIL",
            birthday="1990-01-01",
            is_active=True,
        )

        # 테스트용 유저 생성 (일반인/권한 없음)
        self.general_user = User.objects.create_user(
            email="general@ozcoding.com",
            password="password123",
            name="test2",
            nickname="일반유저",
            role="USER",
            gender="FEMAIL",
            birthday="1995-05-05",
            is_active=True,
        )

        # URL 설정 이름 확인
        self.url = reverse("question-list-create")

    def _get_auth_header(self, user: Any) -> dict[str, Any]:
        """유저 객체를 받아 JWT 액세스 토큰을 생성, HTTP_AUTHORIZATION 헤더 딕셔너리를 반환"""
        refresh = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}

    def test_create_question_success(self) -> None:
        """[성공] 수강생 권한으로 유효한 데이터를 전송 시 질문 등록 확인"""
        auth_header = self._get_auth_header(self.student_user)

        data = {
            "title": "장고 질문입니다.",
            "content": "이 에러는 어떻게 해결하나요?",
            "category_id": self.category.id,
        }

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_data["message"], "질문이 성공적으로 등록되었습니다.")
        self.assertIn("question_id", res_data)
        self.assertTrue(Question.objects.filter(id=res_data["question_id"]).exists())

    def test_create_question_unauthorized(self) -> None:
        """[실패] 로그인하지 않은 경우 (토큰이 없는 경우) 401 에러를 반환 검증"""
        data = {"title": "비회원 질문", "content": "내용", "category_id": self.category.id}

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error_detail"], "로그인한 수강생만 질문을 등록할 수 있습니다.")

    def test_create_question_forbidden(self) -> None:
        """[실패] 수강생이 아닌 유저의 요청 시 403 에러 반환 검증"""
        auth_header = self._get_auth_header(self.general_user)

        data = {"title": "일반인 질문", "content": "내용", "category_id": self.category.id}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_detail"], "질문 등록 권한이 없습니다.")

    def test_create_question_invalid_category(self) -> None:
        """[실패] 존재하지 않는 카테고리 ID 전송 시 400 에러 반환 검증"""
        auth_header = self._get_auth_header(self.student_user)

        data = {"title": "에러 질문", "content": "내용", "category_id": 9999}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, QuestionBaseException.status_code)
        self.assertEqual(response.json()["error_detail"], "유효하지 않은 질문 등록 요청입니다.")

    def test_create_question_bad_request(self) -> None:
        """[실패] 필수 데이터 누락 시 400 에러 반환 검증"""
        auth_header = self._get_auth_header(self.student_user)

        # 필수 필드인 title 누락
        data = {"content": "제목이 없어요", "category_id": self.category.id}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )
        res_data = response.json()

        self.assertEqual(response.status_code, QuestionBaseException.status_code)
        self.assertEqual(res_data["error_detail"], "유효하지 않은 질문 등록 요청입니다.")

    def test_create_question_performance(self) -> None:
        """[성공] 질문 등록 시 발생하는 쿼리 수 검증"""

        auth_header = self._get_auth_header(self.student_user)
        data = {
            "title": "성능 테스트 질문",
            "content": "내용",
            "category_id": self.category.id,
        }

        # 쿼리 발생 내역 캡처
        with CaptureQueriesContext(connection) as context:
            self.client.post(
                self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
            )

        self.assertLessEqual(len(context), 6, f"Expected 6 or fewer queries, but got {len(context)}")
