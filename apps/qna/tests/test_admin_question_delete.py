from typing import Any

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.qna.constants import ErrorMessages
from apps.qna.models import (
    Answer,
    AnswerComment,
    AnswerImage,
    Question,
    QuestionCategory,
    QuestionImage,
)

User = get_user_model()


class AdminQuestionDeleteAPITest(TestCase):
    """
    어드민 질의응답 삭제 API (DELETE) 테스트
    - 성공 케이스
        - 관리자(ADMIN)가 답변/댓글이 있는 질문 삭제 → 200, 카운트 검증
        - 스태프(TA)가 질문 삭제 → 200
        - 답변/댓글이 없는 질문 삭제 → 200, counts = 0
        - 삭제 후 DB에서 Question, Answer, AnswerComment 완전 제거 확인
        - 삭제 후 QuestionImage, AnswerImage도 제거 확인
    - 실패 케이스
        - 401 Unauthorized: 로그인하지 않은 유저
        - 403 Forbidden: 수강생(STUDENT) 유저
        - 404 Not Found: 존재하지 않는 question_id
    """

    def setUp(self) -> None:
        self.client = Client()

        # 카테고리
        self.category = QuestionCategory.objects.create(name="백엔드")

        # 유저 생성
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="password123",
            name="관리자",
            nickname="관리자닉",
            phone_number="010-0000-0000",
            role="ADMIN",
            gender="MALE",
            birthday="1990-01-01",
            is_active=True,
        )

        self.ta_user = User.objects.create_user(
            email="ta@test.com",
            password="password123",
            name="조교",
            nickname="조교닉",
            phone_number="010-1111-1111",
            role="TA",
            gender="MALE",
            birthday="1990-01-01",
            is_active=True,
        )

        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="password123",
            name="수강생",
            nickname="수강생닉",
            phone_number="010-2222-2222",
            role="STUDENT",
            gender="MALE",
            birthday="1995-01-01",
            is_active=True,
        )

        # 질문 (답변/댓글/이미지 포함)
        self.question_with_answers = Question.objects.create(
            title="테스트 질문",
            content="테스트 내용",
            category=self.category,
            author=self.student_user,
        )
        # 질문 이미지
        QuestionImage.objects.create(
            question=self.question_with_answers,
            img_url="https://cdn.example.com/qna/img_01.png",
        )
        # 답변 2개
        self.answer1 = Answer.objects.create(
            question=self.question_with_answers,
            author=self.ta_user,
            content="답변 1",
        )
        self.answer2 = Answer.objects.create(
            question=self.question_with_answers,
            author=self.admin_user,
            content="답변 2",
        )
        # 답변 이미지
        AnswerImage.objects.create(
            answer=self.answer1,
            img_url="https://cdn.example.com/qna/ans_img_01.png",
        )
        # 댓글 3개
        AnswerComment.objects.create(answer=self.answer1, author=self.student_user, content="댓글 1")
        AnswerComment.objects.create(answer=self.answer1, author=self.ta_user, content="댓글 2")
        AnswerComment.objects.create(answer=self.answer2, author=self.student_user, content="댓글 3")

        # 질문 (답변/댓글 없음)
        self.question_without_answers = Question.objects.create(
            title="답변 없는 질문",
            content="내용",
            category=self.category,
            author=self.student_user,
        )

    def _get_auth_header(self, user: Any) -> dict[str, Any]:
        refresh = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}

    def _get_url(self, question_id: int) -> str:
        return reverse("admin-qna-question-delete", kwargs={"question_id": question_id})

    # ==========================================================================
    # 성공 케이스
    # ==========================================================================

    def test_delete_question_with_answers_and_comments(self) -> None:
        """[성공] 관리자가 답변/댓글이 있는 질문 삭제 → 200, 카운트 검증"""
        auth_header = self._get_auth_header(self.admin_user)
        url = self._get_url(self.question_with_answers.id)

        response = self.client.delete(url, **auth_header)
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["question_id"], self.question_with_answers.id)
        self.assertEqual(res_data["deleted_answer_count"], 2)
        self.assertEqual(res_data["deleted_comment_count"], 3)

    def test_delete_question_by_ta_staff(self) -> None:
        """[성공] 스태프(TA)가 질문 삭제 → 200"""
        auth_header = self._get_auth_header(self.ta_user)
        url = self._get_url(self.question_without_answers.id)

        response = self.client.delete(url, **auth_header)
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["question_id"], self.question_without_answers.id)

    def test_delete_question_without_answers(self) -> None:
        """[성공] 답변/댓글이 없는 질문 삭제 → 200, counts = 0"""
        auth_header = self._get_auth_header(self.admin_user)
        url = self._get_url(self.question_without_answers.id)

        response = self.client.delete(url, **auth_header)
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["deleted_answer_count"], 0)
        self.assertEqual(res_data["deleted_comment_count"], 0)

    def test_cascade_deletes_related_records(self) -> None:
        """[성공] 삭제 후 DB에서 Question, Answer, AnswerComment 완전 제거 확인"""
        question_id = self.question_with_answers.id
        auth_header = self._get_auth_header(self.admin_user)
        url = self._get_url(question_id)

        self.client.delete(url, **auth_header)

        self.assertFalse(Question.objects.filter(id=question_id).exists())
        self.assertFalse(Answer.objects.filter(question_id=question_id).exists())
        self.assertEqual(AnswerComment.objects.filter(answer__question_id=question_id).count(), 0)

    def test_cascade_deletes_images(self) -> None:
        """[성공] 삭제 후 QuestionImage, AnswerImage도 제거 확인"""
        question_id = self.question_with_answers.id
        auth_header = self._get_auth_header(self.admin_user)
        url = self._get_url(question_id)

        # 삭제 전 이미지 존재 확인
        self.assertTrue(QuestionImage.objects.filter(question_id=question_id).exists())
        self.assertTrue(AnswerImage.objects.filter(answer__question_id=question_id).exists())

        self.client.delete(url, **auth_header)

        # 삭제 후 이미지 제거 확인
        self.assertFalse(QuestionImage.objects.filter(question_id=question_id).exists())
        self.assertFalse(AnswerImage.objects.filter(answer__question_id=question_id).exists())

    # ==========================================================================
    # 실패 케이스
    # ==========================================================================

    def test_unauthorized(self) -> None:
        """[실패] 로그인하지 않은 경우 401"""
        url = self._get_url(self.question_with_answers.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        res_data = response.json()
        self.assertEqual(res_data["error_detail"], ErrorMessages.UNAUTHORIZED_ADMIN_QUESTION_DELETE.value)

    def test_forbidden_student(self) -> None:
        """[실패] 수강생이 요청한 경우 403"""
        auth_header = self._get_auth_header(self.student_user)
        url = self._get_url(self.question_with_answers.id)

        response = self.client.delete(url, **auth_header)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        res_data = response.json()
        self.assertEqual(res_data["error_detail"], ErrorMessages.FORBIDDEN_ADMIN_QUESTION_DELETE.value)

    def test_not_found_question(self) -> None:
        """[실패] 존재하지 않는 question_id → 404"""
        auth_header = self._get_auth_header(self.admin_user)
        url = self._get_url(999999)

        response = self.client.delete(url, **auth_header)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        res_data = response.json()
        self.assertEqual(res_data["error_detail"], ErrorMessages.NOT_FOUND_ADMIN_QUESTION.value)
