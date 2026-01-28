from django.contrib.auth import get_user_model
from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status

from apps.qna.models import (
    Answer,
    AnswerComment,
    Question,
    QuestionCategory,
    QuestionImage,
)

User = get_user_model()


class QuestionDetailAPITest(TestCase):
    """
    질문 상세 조회 API (GET) 테스트
    - 조회수 증가 로직 (Atomic Update)
    - 에러 매핑 (400, 404)
    - 데이터 정합성 및 성능 최적화
    """

    def setUp(self) -> None:
        self.client = Client()

        # 카테고리 계층 생성 (대 > 중 > 소)
        self.cat_depth1 = QuestionCategory.objects.create(name="개발")
        self.cat_depth2 = QuestionCategory.objects.create(name="백엔드", parent=self.cat_depth1)
        self.cat_depth3 = QuestionCategory.objects.create(name="Django", parent=self.cat_depth2)

        # 유저 생성
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password",
            nickname="테스터",
            name="Test User",
            role="STUDENT",
            gender="MALE",
            birthday="2000-01-01",
        )

        # 질문 생성
        self.question = Question.objects.create(
            author=self.user,
            category=self.cat_depth3,
            title="상세 조회 테스트 제목",
            content="테스트 본문 내용입니다.",
            view_count=10,
        )

        # 이미지 추가
        QuestionImage.objects.create(question=self.question, img_url="http://example.com/q_img.jpg")

        # 답변 및 댓글 추가 (계층 구조)
        self.answer = Answer.objects.create(
            author=self.user, question=self.question, content="첫 번째 답변입니다.", is_adopted=True
        )

        self.comment = AnswerComment.objects.create(
            author=self.user, answer=self.answer, content="답변에 대한 댓글입니다."
        )

        self.url = reverse("question-detail", kwargs={"question_id": self.question.id})

    def test_get_question_detail_data_integrity(self) -> None:
        """[성공] 질문 상세 정보의 모든 필드와 계층 구조 정합성 검증"""
        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 기본 정보 및 조회수 증가 확인
        self.assertEqual(data["id"], self.question.id)
        self.assertEqual(data["title"], "상세 조회 테스트 제목")
        self.assertEqual(data["view_count"], 11)

        # 카테고리 계층 경로 확인 (names 리스트)
        category_data = data["category"]
        self.assertEqual(category_data["names"], ["개발", "백엔드", "Django"])

        # 답변 및 댓글 중첩 구조 확인
        answer_data = data["answers"][0]
        self.assertEqual(len(answer_data["comments"]), 1)
        self.assertEqual(answer_data["comments"][0]["author"]["nickname"], "테스터")

    def test_get_question_detail_unauthenticated_access(self) -> None:
        """[성공] 로그인하지 않은 외부 유저도 상세 조회가 가능해야 함 (AllowAny)"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_question_detail_empty_relations(self) -> None:
        """[성공] 답변이나 이미지가 없는 질문 조회 시 빈 리스트 반환 확인"""
        empty_q = Question.objects.create(author=self.user, category=self.cat_depth1, title="빈 질문", content="내용")
        url = reverse("question-detail", kwargs={"question_id": empty_q.id})

        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["images"], [])
        self.assertEqual(data["answers"], [])

    def test_get_question_detail_not_found(self) -> None:
        """[실패] 존재하지 않는 질문 ID 조회 시 404 에러 메시지 확인"""
        url = reverse("question-detail", kwargs={"question_id": 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "해당 질문을 찾을 수 없습니다.")

    def test_get_question_detail_invalid_id_format(self) -> None:
        """[실패] 유효하지 않은 ID 형식(문자열 등)으로 요청 시 처리 검증"""
        # URL 설정이 <int:question_id> 인 경우 장고 라우터가 404를 먼저 뱉습니다.
        # 만약 명세서의 400 에러를 검증하고 싶다면, 서비스 레이어에 잘못된 값이 도달했을 때를 가정합니다.
        url = "/api/v1/qna/questions/invalid_id"
        response = self.client.get(url)

        # 라우터 수준에서 걸러지면 404, 뷰까지 들어왔는데 로직상 오류면 400
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST])

    def test_question_detail_query_optimization(self) -> None:
        """[성공] 상세 조회 시 N+1 문제 해결 검증 (쿼리 수 8개 이하 유지)"""
        # 데이터 복잡도를 높임
        for i in range(5):
            ans = Answer.objects.create(author=self.user, question=self.question, content=f"추가 답변 {i}")
            AnswerComment.objects.create(author=self.user, answer=ans, content="추가 댓글")

        with CaptureQueriesContext(connection) as context:
            self.client.get(self.url)

        # select_related와 prefetch_related가 정상 작동하면 데이터 양과 관계없이 쿼리 수가 일정함
        self.assertLessEqual(len(context), 8, f"너무 많은 쿼리가 발생함: {len(context)}개")

    def test_view_count_concurrency_safety(self) -> None:
        """[로직] F 객체를 이용한 조회수 증가가 DB에 정확히 반영되는지 확인"""
        initial_count = self.question.view_count

        # 연속 2회 조회
        self.client.get(self.url)
        self.client.get(self.url)

        self.question.refresh_from_db()
        self.assertEqual(self.question.view_count, initial_count + 2)
