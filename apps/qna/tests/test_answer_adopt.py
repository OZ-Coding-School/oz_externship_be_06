from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.constants import ErrorMessages
from apps.qna.models import Answer, Question, QuestionCategory
from apps.qna.tests.factories import create_student_user
from apps.users.models import User


class AnswerAdoptTest(APITestCase):
    """
    답변 채택 API (POST) 테스트
    - 성공 케이스
        - 본인이 작성한 질문의 답변 채택
    - 실패 케이스
        - 401 Unauthorized: 로그인하지 않은 유저
        - 403 Forbidden: 본인이 작성한 질문이 아닌 경우
        - 404 Not Found: 존재하지 않는 답변
        - 409 Conflict: 이미 채택된 답변이 존재
    - 성능 테스트 (쿼리 수 검증)
    """

    author: User
    answerer: User
    other_user: User
    category: QuestionCategory
    question: Question
    answer: Answer
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        # 테스트용 유저 - 질문 작성자 (수강생)
        cls.author = create_student_user()
        # 테스트용 유저 - 답변 작성자 (다른 수강생)
        cls.answerer = create_student_user()
        # 테스트용 유저 - 제3자 (권한 없는 유저)
        cls.other_user = create_student_user()

        # 카테고리 생성
        cls.category = QuestionCategory.objects.create(name="Django", parent=None)

        # 질문 생성
        cls.question = Question.objects.create(
            title="질문 제목", content="질문 내용", category=cls.category, author=cls.author
        )

        # 답변 생성 (is_adopted가 테스트에서 변경되므로 매 테스트마다 새로 생성)
        cls.answer = Answer.objects.create(question=cls.question, author=cls.answerer, content="답변 내용")

        # URL
        cls.url = reverse("answer-adopt", kwargs={"answer_id": cls.answer.id})

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.author)

    # ==========================================================================
    # 성공 케이스
    # ==========================================================================
    def test_adopt_answer_success(self) -> None:
        """[200] 본인이 작성한 질문의 답변 채택"""
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["question_id"], self.question.id)
        self.assertEqual(response.data["answer_id"], self.answer.id)
        self.assertTrue(response.data["is_adopted"])

        # DB 확인
        self.answer.refresh_from_db()
        self.assertTrue(self.answer.is_adopted)

    # ==========================================================================
    # 실패 케이스
    # ==========================================================================
    def test_adopt_answer_unauthorized(self) -> None:
        """[401] 로그인하지 않은 사용자"""
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], ErrorMessages.UNAUTHORIZED_ANSWER_ADOPT.value)

    def test_adopt_answer_forbidden(self) -> None:
        """[403] 본인이 작성한 질문이 아닌 경우"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], ErrorMessages.FORBIDDEN_ANSWER_ADOPT.value)

    def test_adopt_answer_not_found(self) -> None:
        """[404] 존재하지 않는 답변 ID"""
        url = reverse("answer-adopt", kwargs={"answer_id": 99999})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], ErrorMessages.NOT_FOUND_QUESTION_OR_ANSWER.value)

    def test_adopt_answer_conflict(self) -> None:
        """[409] 이미 채택된 답변 존재"""
        # 먼저 채택 성공
        self.answer.is_adopted = True
        self.answer.save()

        # 다른 답변 생성 (또는 같은 답변이라도 채택 시도)
        # 같은 답변을 다시 채택 시도해도 이미 채택된 답변이 질문에 존재하므로 409
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["error_detail"], ErrorMessages.ALREADY_EXISTS_ANSWER_ADOPT.value)

    # ==========================================================================
    # 성능 테스트
    # ==========================================================================
    def test_performance_query_count(self) -> None:
        """[성능] 쿼리 수 검증
        1. transaction.atomic SAVEPOINT
        2. Answer 조회 (select_for_update)
        3. 이미 채택된 답변 존재 확인 (Answer filter exists)
        4. Answer Update (is_adopted=True)
        5. RELEASE SAVEPOINT
        Total: 5 queries expected
        """

        # 쿼리 수 확인
        with self.assertNumQueries(5):
            self.client.post(self.url)
