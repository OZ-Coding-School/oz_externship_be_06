from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.constants import ErrorMessages
from apps.qna.models import Answer, AnswerComment, Question, QuestionCategory
from apps.users.models import User


class AnswerCommentCreateTest(APITestCase):
    def setUp(self) -> None:
        # 유저 생성 (수강생)
        self.user = User.objects.create_user(
            email="student@example.com",
            password="password!@#",
            name="test1",
            nickname="student",
            phone_number="010-1234-5678",
            gender="MALE",
            birthday="2000-01-01",
            role="STUDENT",
        )
        # 테스트용 유저 생성 (일반인/권한 없음)
        self.general_user = User.objects.create_user(
            email="general@ozcoding.com",
            password="password123",
            name="test2",
            nickname="general",
            role="USER",
            gender="FEMAIL",
            birthday="1995-05-05",
            is_active=True,
        )

        self.client.force_authenticate(user=self.user)

        # 카테고리 생성
        self.category = QuestionCategory.objects.create(name="Django", parent=None)

        # 질문 생성
        self.question = Question.objects.create(
            title="질문 제목", content="질문 내용", category=self.category, author=self.user
        )

        # 답변 생성
        self.answer = Answer.objects.create(question=self.question, author=self.user, content="답변 내용")

        # URL
        self.url = reverse("answer-comment-create", kwargs={"answer_id": self.answer.id})

    def test_create_comment_success(self) -> None:
        """
        [성공] 유효한 데이터로 댓글 생성 성공 (201 Created)
        """
        data = {"content": "감사합니다. 많은 도움이 되었습니다."}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["answer_id"], self.answer.id)
        self.assertEqual(response.data["author_id"], self.user.id)
        self.assertTrue(AnswerComment.objects.filter(id=response.data["comment_id"]).exists())

    def test_create_comment_unauthorized(self) -> None:
        """
        [실패] 로그인하지 않은 사용자 (401 Unauthorized)
        """
        self.client.force_authenticate(user=None)
        data = {"content": "댓글 내용"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], ErrorMessages.UNAUTHORIZED_COMMENT_CREATE.value)

    def test_create_comment_forbidden(self) -> None:
        """[실패] 허용되지 않은 Role(USER)로 요청 시 403 반환 검증"""
        # auth_header = self._get_auth_header(self.regular_user)
        self.client.force_authenticate(user=self.general_user)
        data = {"content": "댓글 내용"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.FORBIDDEN_COMMENT_CREATE.value)

    def test_create_comment_invalid_content_blank(self) -> None:
        """
        [실패] 댓글 내용이 비어있음 (400 Bad Request)
        """
        data = {"content": ""}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], ErrorMessages.INVALID_COMMENT_BLANK.value)

    def test_create_comment_invalid_content_too_long(self) -> None:
        """
        [실패] 댓글 내용 500자 초과 (400 Bad Request)
        """
        data = {"content": "a" * 501}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], ErrorMessages.INVALID_COMMENT_LENGTH_LIMIT.value)

    def test_create_comment_not_found_answer(self) -> None:
        """
        [실패] 존재하지 않는 답변 ID (404 Not Found)
        """
        url = reverse("answer-comment-create", kwargs={"answer_id": 99999})
        data = {"content": "댓글 내용"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], ErrorMessages.NOT_FOUND_ANSWER.value)

    def test_performance_query_count(self) -> None:
        """
        [Performance] 쿼리 수 검증
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
