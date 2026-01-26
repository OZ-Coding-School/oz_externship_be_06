import json

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status

from apps.qna.models import Answer, Question, QuestionCategory

User = get_user_model()


class QuestionListAPITest(TestCase):
    """
    질문 목록 조회 API (GET) 테스트
    - 검색, 필터링, 정렬 및 페이지네이션 검증
    """

    def setUp(self) -> None:
        # Django 내장 TestClient 초기화
        self.client = Client()

        # 테스트용 카테고리 생성 (계층형)
        self.category_fe = QuestionCategory.objects.create(name="프론트엔드")
        self.category_react = QuestionCategory.objects.create(name="React", parent=self.category_fe)
        self.category_be = QuestionCategory.objects.create(name="백엔드")

        # 테스트용 유저 생성
        self.user = User.objects.create_user(
            email="tester@ozcoding.com",
            password="password123",
            name="김테스터",
            nickname="테스터",
            role="STUDENT",
            gender="MALE",
            birthday="1990-01-01",
        )

        # 테스트용 질문 데이터 대량 생성 (페이지네이션 및 필터링용)
        # Q1: React 카테고리, 이미지 포함, 답변 없음 (waiting)
        self.q1 = Question.objects.create(
            author=self.user,
            category=self.category_react,
            title="React Hooks 질문",
            content="![thumb](https://example.com/image.png) useEffect 사용법이 궁금해요.",
        )

        # Q2: 백엔드 카테고리, 답변 있음 (answered)
        self.q2 = Question.objects.create(
            author=self.user,
            category=self.category_be,
            title="Django ORM 성능 최적화",
            content="select_related와 prefetch_related의 차이는 무엇인가요?",
        )
        # Q2에 대한 답변 생성
        Answer.objects.create(author=self.user, question=self.q2, content="답변입니다.")

        # URL 설정
        self.url = reverse("question-list-create")

    def test_get_question_list_success(self) -> None:
        """[성공] 필터 없이 전체 목록 조회 시 최신순으로 반환되어야 함"""
        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # QnAPagination 구조 확인 (results 키 포함 여부)
        self.assertIn("results", data)
        # 최신순 정렬 확인 (최근 생성된 q2가 첫 번째)
        self.assertEqual(data["results"][0]["id"], self.q2.id)
        # 썸네일 파싱 확인 (q1의 content에서 추출)
        self.assertEqual(data["results"][1]["thumbnail_img_url"], "https://example.com/image.png")

    def test_filter_by_category(self) -> None:
        """[성공] 특정 카테고리 ID로 필터링 시 해당 질문만 반환되어야 함"""
        response = self.client.get(self.url, {"category_id": self.category_be.id})
        data = response.json()

        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["title"], "Django ORM 성능 최적화")

    def test_search_by_keyword(self) -> None:
        """[성공] 검색어 입력 시 제목 또는 내용에서 검색되어야 함"""
        response = self.client.get(self.url, {"search_keyword": "Hooks"})
        data = response.json()

        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["title"], "React Hooks 질문")

    def test_filter_by_answer_status_waiting(self) -> None:
        """[성공] answer_status가 'waiting'인 경우 답변이 없는 질문만 반환"""
        response = self.client.get(self.url, {"answer_status": "waiting"})
        data = response.json()

        # 답변이 없는 q1만 나와야 함
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["id"], self.q1.id)

    def test_filter_by_answer_status_answered(self) -> None:
        """[성공] answer_status가 'answered'인 경우 답변이 1개 이상인 질문만 반환"""
        response = self.client.get(self.url, {"answer_status": "answered"})
        data = response.json()

        # 답변이 있는 q2만 나와야 함
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["id"], self.q2.id)

    def test_pagination_size(self) -> None:
        """[성공] size 파라미터에 따라 반환되는 데이터 개수가 조절되어야 함"""
        # 테스트를 위해 추가 데이터 생성
        for i in range(5):
            Question.objects.create(author=self.user, category=self.category_be, title=f"추가 질문 {i}", content="내용")

        response = self.client.get(self.url, {"size": 3})
        data = response.json()

        self.assertEqual(len(data["results"]), 3)
        self.assertIsNotNone(data["next"])  # 다음 페이지 링크 확인

    def test_question_list_performance(self) -> None:
        """[성공] 질문 목록 조회 시 발생하는 쿼리 수 검증"""

        # 쿼리 발생 내역 캡처
        with CaptureQueriesContext(connection) as context:
            self.client.get(self.url)

        self.assertEqual(len(context), 2, f"Expected 2 or fewer queries, but got {len(context)}")
