from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.models import Answer, AnswerComment, Question, QuestionCategory
from apps.qna.models.answer_image import AnswerImage
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
    """

    def setUp(self) -> None:
        # 유저 생성 variables
        self.email = "admin@example.com"
        self.password = "password123!"
        self.nickname = "admin"
        self.name = "Admin"
        self.phone_number = "01012341234"

        # Admin 유저 생성
        self.admin_user = User.objects.create_superuser(
            email=self.email,
            password=self.password,
            nickname=self.nickname,
            name=self.name,
            phone_number=self.phone_number,
            birthday="2000-01-01",
        )

        # Staff(TA) 유저 생성
        self.staff_user = User.objects.create_user(
            email="staff@example.com",
            password="password123!",
            nickname="staff_ta",
            name="StaffTA",
            phone_number="01012345678",
            birthday="2000-01-01",
        )
        self.staff_user.is_staff = True
        self.staff_user.save()

        # 일반 유저 생성
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="password123!",
            nickname="student",
            name="Student",
            phone_number="01012341234",
            birthday="2000-01-01",
        )

        # 카테고리 생성
        self.category = QuestionCategory.objects.create(name="Python")

        # 질문 생성
        self.question = Question.objects.create(
            category=self.category,
            author=self.student_user,
            title="테스트 질문",
            content="테스트 질문 내용입니다.",
        )

        # 답변 생성
        self.answer = Answer.objects.create(
            question=self.question,
            author=self.student_user,
            content="테스트 답변입니다.",
        )

        # 댓글 생성
        self.comment = AnswerComment.objects.create(
            answer=self.answer,
            author=self.student_user,
            content="테스트 댓글입니다.",
        )

        # 답변 이미지 생성
        self.answer_image = AnswerImage.objects.create(
            answer=self.answer,
            img_url="https://example.com/image.png",
        )

        self.url = reverse("admin-qna-answer-delete", kwargs={"answer_id": self.answer.id})

    def test_delete_answer_success(self) -> None:
        """[성공] 관리자(ADMIN)가 답변/댓글이 있는 답변 삭제 → 200, 카운트 검증"""
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
        """[성공] 스태프(TA)가 답변 삭제 → 200"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Answer.objects.filter(id=self.answer.id).exists())

    def test_delete_answer_no_comments(self) -> None:
        """[성공] 댓글이 없는 답변 삭제 → 200, counts = 0"""
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

    def test_delete_answer_not_found(self) -> None:
        """[실패] 존재하지 않는 answer_id → 404"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("admin-qna-answer-delete", kwargs={"answer_id": 9999})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_answer_forbidden_student(self) -> None:
        """[실패] 수강생(STUDENT) 유저 → 403"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_answer_unauthorized(self) -> None:
        """[실패] 로그인하지 않은 경우 → 401"""
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
