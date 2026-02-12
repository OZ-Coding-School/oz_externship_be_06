from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.constants import ErrorMessages
from apps.qna.models import Answer, AnswerComment, Question, QuestionCategory
from apps.qna.tests.factories import create_general_user, create_student_user
from apps.users.models import User


class AnswerCommentCreateTest(APITestCase):
    """
    답변 댓글 등록 API (POST) 테스트
    - 성공 케이스
        - 유효한 데이터로 댓글 생성 성공
    - 실패 케이스
        - 401 Unauthorized: 로그인하지 않은 유저
        - 403 Forbidden: 허용되지 않은 Role (USER)
        - 400 Bad Request: 댓글 내용 비어있음 또는 500자 초과
        - 404 Not Found: 존재하지 않는 답변
    - 성능 테스트 (쿼리 수 검증)
    """

    student_user: User
    general_user: User
    category: QuestionCategory
    question: Question
    answer: Answer
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        # 테스트용 유저
        cls.student_user = create_student_user()
        cls.general_user = create_general_user()

        # 카테고리 생성
        cls.category = QuestionCategory.objects.create(name="Django", parent=None)

        # 질문 생성
        cls.question = Question.objects.create(
            title="질문 제목", content="질문 내용", category=cls.category, author=cls.student_user
        )

        # 답변 생성
        cls.answer = Answer.objects.create(question=cls.question, author=cls.student_user, content="답변 내용")

        # URL
        cls.url = reverse("answer-comment-create", kwargs={"answer_id": cls.answer.id})

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.student_user)

    # ==========================================================================
    # 성공 케이스
    # ==========================================================================
    def test_create_comment_success(self) -> None:
        """[201] 유효한 데이터로 댓글 생성"""
        data = {"content": "감사합니다. 많은 도움이 되었습니다."}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["answer_id"], self.answer.id)
        self.assertEqual(response.data["author_id"], self.student_user.id)
        self.assertTrue(AnswerComment.objects.filter(id=response.data["comment_id"]).exists())

    # ==========================================================================
    # 실패 케이스
    # ==========================================================================
    def test_create_comment_unauthorized(self) -> None:
        """[401] 로그인하지 않은 사용자"""
        self.client.force_authenticate(user=None)
        data = {"content": "댓글 내용"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], ErrorMessages.UNAUTHORIZED_COMMENT_CREATE.value)

    def test_create_comment_forbidden(self) -> None:
        """[403] 허용되지 않은 Role(USER)로 요청"""
        # auth_header = self._get_auth_header(self.regular_user)
        self.client.force_authenticate(user=self.general_user)
        data = {"content": "댓글 내용"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.FORBIDDEN_COMMENT_CREATE.value)

    def test_create_comment_invalid_content_blank(self) -> None:
        """[400] 댓글 내용이 비어있음"""
        data = {"content": ""}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], ErrorMessages.INVALID_COMMENT_BLANK.value)

    def test_create_comment_invalid_content_too_long(self) -> None:
        """[400] 댓글 내용 500자 초과"""
        data = {"content": "a" * 501}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], ErrorMessages.INVALID_COMMENT_LENGTH_LIMIT.value)

    def test_create_comment_not_found_answer(self) -> None:
        """[404] 존재하지 않는 답변 ID"""
        url = reverse("answer-comment-create", kwargs={"answer_id": 99999})
        data = {"content": "댓글 내용"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], ErrorMessages.NOT_FOUND_ANSWER.value)

    # ==========================================================================
    # 성능 테스트
    # ==========================================================================
    def test_performance_query_count(self) -> None:
        """[성능] 쿼리 수 검증
        1. create_comment의 transaction.atomic으로 인한 SAVEPOINT
        2. Answer 조회 (select_for_update)
        3. Comment Insert
        4. RELEASE SAVEPOINT
        Total: 4 queries expected
        """
        data = {"content": "성능 테스트 댓글"}

        # 쿼리 수 확인
        with self.assertNumQueries(4):
            self.client.post(self.url, data)
