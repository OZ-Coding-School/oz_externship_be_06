from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.constants import ErrorMessages
from apps.qna.models import (
    Answer,
    AnswerComment,
    AnswerImage,
    Question,
    QuestionCategory,
    QuestionImage,
)
from apps.qna.tests.factories import (
    create_admin_user,
    create_student_user,
    create_ta_user,
)
from apps.users.models import User


class AdminQuestionDeleteAPITest(APITestCase):
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

    admin_user: User
    ta_user: User
    student_user: User
    category: QuestionCategory
    question_with_answers: Question
    question_without_answers: Question
    answer1: Answer
    answer2: Answer
    url: str
    url_without_answers: str
    not_found_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        # 유저 생성
        cls.admin_user = create_admin_user()
        cls.ta_user = create_ta_user()
        cls.student_user = create_student_user()

        # 카테고리
        cls.category = QuestionCategory.objects.create(name="백엔드")

        # 질문 (답변/댓글/이미지 포함)
        cls.question_with_answers = Question.objects.create(
            title="테스트 질문",
            content="테스트 내용",
            category=cls.category,
            author=cls.student_user,
        )
        # 질문 이미지
        QuestionImage.objects.create(
            question=cls.question_with_answers,
            img_url="https://cdn.example.com/qna/img_01.png",
        )
        # 답변 2개
        cls.answer1 = Answer.objects.create(
            question=cls.question_with_answers,
            author=cls.ta_user,
            content="답변 1",
        )
        cls.answer2 = Answer.objects.create(
            question=cls.question_with_answers,
            author=cls.admin_user,
            content="답변 2",
        )
        # 답변 이미지
        AnswerImage.objects.create(
            answer=cls.answer1,
            img_url="https://cdn.example.com/qna/ans_img_01.png",
        )
        # 댓글 3개
        AnswerComment.objects.create(answer=cls.answer1, author=cls.student_user, content="댓글 1")
        AnswerComment.objects.create(answer=cls.answer1, author=cls.ta_user, content="댓글 2")
        AnswerComment.objects.create(answer=cls.answer2, author=cls.student_user, content="댓글 3")

        # 질문 (답변/댓글 없음)
        cls.question_without_answers = Question.objects.create(
            title="답변 없는 질문",
            content="내용",
            category=cls.category,
            author=cls.student_user,
        )

        # URL
        cls.url = reverse("admin-qna-question-detail", kwargs={"question_id": cls.question_with_answers.id})
        cls.url_without_answers = reverse(
            "admin-qna-question-detail",
            kwargs={"question_id": cls.question_without_answers.id},
        )
        cls.not_found_url = reverse("admin-qna-question-detail", kwargs={"question_id": 999999})

    # ==========================================================================
    # 성공 케이스
    # ==========================================================================
    def test_delete_question_with_answers_and_comments(self) -> None:
        """[200] 관리자가 답변/댓글이 있는 질문 삭제 → 카운트 검증"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.url)
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["question_id"], self.question_with_answers.id)
        self.assertEqual(res_data["deleted_answer_count"], 2)
        self.assertEqual(res_data["deleted_comment_count"], 3)

    def test_delete_question_by_ta_staff(self) -> None:
        """[200] 스태프(TA)가 질문 삭제"""
        self.client.force_authenticate(user=self.ta_user)
        response = self.client.delete(self.url_without_answers)
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["question_id"], self.question_without_answers.id)

    def test_delete_question_without_answers(self) -> None:
        """[200] 답변/댓글이 없는 질문 삭제 → counts = 0"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.url_without_answers)
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["deleted_answer_count"], 0)
        self.assertEqual(res_data["deleted_comment_count"], 0)

    def test_cascade_deletes_related_records(self) -> None:
        """[200] 삭제 후 DB에서 Question, Answer, AnswerComment 완전 제거"""
        self.client.force_authenticate(user=self.admin_user)
        question_id = self.question_with_answers.id
        self.client.delete(self.url)

        self.assertFalse(Question.objects.filter(id=question_id).exists())
        self.assertFalse(Answer.objects.filter(question_id=question_id).exists())
        self.assertEqual(AnswerComment.objects.filter(answer__question_id=question_id).count(), 0)

    def test_cascade_deletes_images(self) -> None:
        """[200] 삭제 후 QuestionImage, AnswerImage도 제거"""
        self.client.force_authenticate(user=self.admin_user)
        question_id = self.question_with_answers.id

        # 삭제 전 이미지 존재 확인
        self.assertTrue(QuestionImage.objects.filter(question_id=question_id).exists())
        self.assertTrue(AnswerImage.objects.filter(answer__question_id=question_id).exists())

        self.client.delete(self.url)

        # 삭제 후 이미지 제거 확인
        self.assertFalse(QuestionImage.objects.filter(question_id=question_id).exists())
        self.assertFalse(AnswerImage.objects.filter(answer__question_id=question_id).exists())

    # ==========================================================================
    # 실패 케이스
    # ==========================================================================
    def test_unauthorized(self) -> None:
        """[401] 로그인하지 않은 경우"""
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        res_data = response.json()
        self.assertEqual(res_data["error_detail"], ErrorMessages.UNAUTHORIZED_ADMIN_QUESTION_DELETE.value)

    def test_forbidden_student(self) -> None:
        """[403] 수강생이 요청한 경우"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        res_data = response.json()
        self.assertEqual(res_data["error_detail"], ErrorMessages.FORBIDDEN_ADMIN_QUESTION_DELETE.value)

    def test_not_found_question(self) -> None:
        """[404] 존재하지 않는 question_id"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.not_found_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        res_data = response.json()
        self.assertEqual(res_data["error_detail"], ErrorMessages.NOT_FOUND_ADMIN_QUESTION.value)
