from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.models import Answer, AnswerComment, Question, QuestionCategory
from apps.qna.models.answer_image import AnswerImage
from apps.qna.tests.factories import (
    create_admin_user,
    create_general_user,
    create_ta_user,
)
from apps.users.models import User


class AdminAnswerDeleteAPITest(APITestCase):
    """
    어드민 답변 삭제 API (DELETE) 테스트
    - 성공 케이스
        - 관리자(ADMIN)가 댓글이 있는 답변 삭제 → 200, 카운트 검증
        - 스태프(TA)가 답변 삭제 → 200
        - 댓글이 없는 답변 삭제 → 200, counts = 0
        - 삭제 후 DB에서 Answer, AnswerComment 완전 제거 확인
        - 삭제 후 AnswerImage도 제거 확인
    - 실패 케이스
        - 401 Unauthorized: 로그인하지 않은 유저
        - 403 Forbidden: 수강생(STUDENT) 유저
        - 404 Not Found: 존재하지 않는 answer_id
        - 404 Not Found: answer_id가 int가 아닌 str인 경우
    """

    admin_user: User
    staff_user: User
    student_user: User
    category: QuestionCategory
    question: Question
    answer: Answer
    comment: AnswerComment
    answer_image: AnswerImage
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        # 테스트용 유저
        cls.admin_user = create_admin_user()
        cls.staff_user = create_ta_user()
        cls.staff_user.is_staff = True
        cls.staff_user.save()
        cls.student_user = create_general_user()

        # 카테고리 생성
        cls.category = QuestionCategory.objects.create(name="Python")

        # 질문 생성
        cls.question = Question.objects.create(
            category=cls.category,
            author=cls.student_user,
            title="테스트 질문",
            content="테스트 질문 내용입니다.",
        )

        # 답변 생성
        cls.answer = Answer.objects.create(
            question=cls.question,
            author=cls.student_user,
            content="테스트 답변입니다.",
        )

        # 댓글 생성
        cls.comment = AnswerComment.objects.create(
            answer=cls.answer,
            author=cls.student_user,
            content="테스트 댓글입니다.",
        )

        # 답변 이미지 생성
        cls.answer_image = AnswerImage.objects.create(
            answer=cls.answer,
            img_url="https://example.com/image.png",
        )

        # URL
        cls.url = reverse("admin-qna-answer-delete", kwargs={"answer_id": cls.answer.id})

    # ==========================================================================
    # 성공 케이스
    # ==========================================================================
    def test_delete_answer_success(self) -> None:
        """[200] 관리자(ADMIN)가 답변/댓글이 있는 답변 삭제 → 카운트 검증"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["answer_id"], self.answer.id)
        self.assertEqual(response.data["deleted_comment_count"], 1)

        # DB에서 삭제 확인
        self.assertFalse(Answer.objects.filter(id=self.answer.id).exists())
        self.assertFalse(AnswerComment.objects.filter(id=self.comment.id).exists())
        self.assertFalse(AnswerImage.objects.filter(id=self.answer_image.id).exists())

    def test_delete_answer_success_staff_ta(self) -> None:
        """[200] 스태프(TA)가 답변 삭제"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Answer.objects.filter(id=self.answer.id).exists())

    def test_delete_answer_no_comments(self) -> None:
        """[200] 댓글이 없는 답변 삭제 → counts = 0"""
        # 댓글 없는 답변 생성
        answer_no_comments = Answer.objects.create(
            question=self.question,
            author=self.student_user,
            content="댓글 없는 답변",
        )
        url = reverse("admin-qna-answer-delete", kwargs={"answer_id": answer_no_comments.id})

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["deleted_comment_count"], 0)
        self.assertFalse(Answer.objects.filter(id=answer_no_comments.id).exists())

    # ==========================================================================
    # 실패 케이스
    # ==========================================================================
    def test_delete_answer_not_found(self) -> None:
        """[404] 존재하지 않는 answer_id"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("admin-qna-answer-delete", kwargs={"answer_id": 9999})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_answer_forbidden_student(self) -> None:
        """[403] 수강생(STUDENT) 유저"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_answer_unauthorized(self) -> None:
        """[401] 로그인하지 않은 경우"""
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_answer_invalid_id_type_string(self) -> None:
        """[404] answer_id가 int가 아닌 str인 경우"""
        self.client.force_authenticate(user=self.admin_user)
        url = "/api/v1/admin/qna/answers/invalid_string_id"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
