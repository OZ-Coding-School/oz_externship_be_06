import json

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status

from apps.qna.exceptions.question_exception import QuestionNotFoundException
from apps.qna.models import Answer, Question, QuestionCategory

User = get_user_model()


class QuestionListAPITest(TestCase):
    """
    질문 목록 조회 API (GET) 테스트
    - 검색, 필터링, 정렬 및 페이지네이션 검증
    - 400, 404 에러 매핑 검증
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
            role="USER",
            gender="MALE",
            birthday="1990-01-01",
        )

        # 테스트용 질문
        # Q1: React 카테고리, 이미지 포함, 답변 없음, 조회수 10
        self.q1 = Question.objects.create(
            author=self.user,
            category=self.category_react,
            title="React Hooks 질문",
            content="![thumb](https://example.com/image.png) useEffect 사용법이 궁금해요.",
            view_count=10,
        )

        # Q2: 백엔드 카테고리, 답변 있음, 조회수 50
        self.q2 = Question.objects.create(
            author=self.user,
            category=self.category_be,
            title="Django ORM 성능 최적화",
            content="select_related와 prefetch_related의 차이는 무엇인가요?",
            view_count=50,
        )
        # Q2에 대한 답변 생성
        Answer.objects.create(author=self.user, question=self.q2, content="답변입니다.")

        # URL 설정
        self.url = reverse("question-list-create")

    # --- 성공 케이스 테스트 ---------------------

    def test_get_question_list_success(self) -> None:
        """[성공] 전체 목록 조회 및 정렬(latest) 확인"""
        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # QnAPagination 구조 확인 (results 키 포함 여부)
        self.assertIn("results", data)
        # 최신순 정렬 확인 (최근 생성된 q2가 첫 번째)
        self.assertEqual(data["results"][0]["id"], self.q2.id)

    def test_get_question_list_most_views_sort(self) -> None:
        """[성공] 조회수순(most_views) 정렬 확인"""
        response = self.client.get(self.url, {"sort": "most_views"})
        data = response.json()

        # 조회수가 높은 q2(50)가 q1(10)보다 먼저 나와야 함
        self.assertEqual(data["results"][0]["id"], self.q2.id)
        self.assertEqual(data["results"][0]["view_count"], 50)

    def test_filter_by_category(self) -> None:
        """[성공] 특정 카테고리 ID로 필터링 확인"""
        response = self.client.get(self.url, {"category_id": self.category_be.id})
        data = response.json()

        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["title"], "Django ORM 성능 최적화")

    def test_search_by_keyword(self) -> None:
        """[성공] 검색어 입력 시 제목 또는 내용에서 검색 확인"""
        # 제목
        response_title = self.client.get(self.url, {"search_keyword": "Hooks"})
        data_title = response_title.json()
        self.assertEqual(len(data_title["results"]), 1)
        self.assertEqual(data_title["results"][0]["id"], self.q1.id)

        # 내용
        response_content = self.client.get(self.url, {"search_keyword": "select_related"})
        data_content = response_content.json()
        self.assertEqual(len(data_content["results"]), 1)
        self.assertEqual(data_content["results"][0]["id"], self.q2.id)

    def test_filter_by_answer_status_waiting(self) -> None:
        """[성공] answer_status가 'waiting'인 경우 답변이 없는 질문 반환 확인"""
        response = self.client.get(self.url, {"answer_status": "waiting"})
        data = response.json()

        # 답변이 없는 q1만 나와야 함
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["id"], self.q1.id)

    def test_filter_by_answer_status_answered(self) -> None:
        """[성공] answer_status가 'answered'인 경우 답변이 1개 이상인 질문 반환 확인"""
        response = self.client.get(self.url, {"answer_status": "answered"})
        data = response.json()

        # 답변이 있는 q2만 나와야 함
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["id"], self.q2.id)

    def test_pagination_size(self) -> None:
        """[성공] size 파라미터에 따라 반환되는 데이터 개수 조절 확인"""
        # 테스트를 위해 추가 데이터 생성
        for i in range(5):
            Question.objects.create(author=self.user, category=self.category_be, title=f"추가 질문 {i}", content="내용")

        response = self.client.get(self.url, {"size": 3})
        data = response.json()

        self.assertEqual(len(data["results"]), 3)
        self.assertIsNotNone(data["next"])  # 다음 페이지 링크 확인

    def test_content_parser_integration(self) -> None:
        """[성공] 썸네일 URL이 올바르게 반환되는지 확인"""
        response = self.client.get(self.url)
        results = response.json()["results"]

        # q1의 썸네일 확인
        q1_data = next(item for item in results if item["id"] == self.q1.id)
        self.assertEqual(q1_data["thumbnail_img_url"], "https://example.com/image.png")

    # --- 404 Not Found ---------------------

    def test_filter_by_invalid_category_returns_404(self) -> None:
        """[404] 존재하지 않는 카테고리 ID로 조회 시 404 반환 검증"""
        response = self.client.get(self.url, {"category_id": 9999})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "조회 가능한 질문이 존재하지 않습니다.")

    def test_search_no_results_returns_404(self) -> None:
        """[404] 검색 결과가 전혀 없을 경우 404 반환 검증"""
        response = self.client.get(self.url, {"search_keyword": "절대로없을법한검색어123"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "조회 가능한 질문이 존재하지 않습니다.")

    def test_filter_status_no_results_returns_404(self) -> None:
        """[404] 필터 조건에 부합하는 데이터가 없을 경우 404 반환 검증"""
        # q1에 답변을 달아서 모든 질문을 'answered' 상태로 만듦
        Answer.objects.create(author=self.user, question=self.q1, content="답변 추가")

        # 'waiting' 상태를 조회하면 결과가 0건이므로 404 발생
        response = self.client.get(self.url, {"answer_status": "waiting"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "조회 가능한 질문이 존재하지 않습니다.")

    # --- 400 Bad Request ---------------------

    def test_invalid_sort_choice_returns_400(self) -> None:
        """[400] 허용되지 않은 sort 옵션 입력 시 400 반환 검증 (ChoiceField 검증)"""
        # 'popular'는 ChoiceField에 없음
        response = self.client.get(self.url, {"sort": "popular"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Mixin에 의해 error_detail에 커스텀 에러 메시지가 담겨있는지 확인
        self.assertEqual(response.json()["error_detail"], "유효하지 않은 목록 조회 요청입니다.")

    def test_invalid_answer_status_choice_returns_400(self) -> None:
        """[400] 허용되지 않은 answer_status 옵션 입력 시 400 반환 검증"""
        response = self.client.get(self.url, {"answer_status": "pending"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error_detail"], "유효하지 않은 목록 조회 요청입니다.")

    def test_invalid_page_type_returns_400(self) -> None:
        """[400] 숫자가 아닌 페이지 번호 입력 시 400 반환 검증(IntegerField 검증)"""
        response = self.client.get(self.url, {"page": "first_page"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error_detail"], "유효하지 않은 목록 조회 요청입니다.")

    def test_question_list_performance(self) -> None:
        """[성공] 질문 목록 조회 시 발생하는 쿼리 수 검증"""
        # 추가 데이터 생성
        for i in range(5):
            Question.objects.create(author=self.user, category=self.category_be, title=f"Q{i}", content="내용")

        # 쿼리 발생 내역 캡처
        with CaptureQueriesContext(connection) as context:
            self.client.get(self.url)

        self.assertLessEqual(len(context), 5, f"Expected 5 or fewer queries, but got {len(context)}")
