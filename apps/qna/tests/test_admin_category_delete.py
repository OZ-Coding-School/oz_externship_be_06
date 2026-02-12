from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.constants import DEFAULT_CATEGORY
from apps.qna.models import Question, QuestionCategory
from apps.qna.tests.factories import create_admin_user, create_student_user
from apps.users.models import User


class AdminCategoryDeleteAPITest(APITestCase):
    """
    어드민 카테고리 삭제 API (DELETE) 테스트
    - 성공 케이스
        - 대분류 삭제 → 하위 카테고리 모두 삭제, 질문은 '일반'으로 이동
        - 중분류 삭제 → 하위 카테고리 모두 삭제, 질문은 '일반'으로 이동
        - 소분류 삭제 → 질문은 '일반'으로 이동
        - '일반' 카테고리 자동 생성 확인
    - 실패 케이스
        - 409 Conflict: '일반' 카테고리 삭제 시도
        - 401 Unauthorized: 로그인하지 않은 유저
        - 403 Forbidden: 일반 유저
        - 404 Not Found: 존재하지 않는 category_id
    """

    admin_user: User
    student_user: User
    large_category: QuestionCategory
    medium_category: QuestionCategory
    small_category: QuestionCategory
    q_large: Question
    q_medium: Question
    q_small: Question
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        # 테스트용 유저
        cls.admin_user = create_admin_user()
        cls.student_user = create_student_user()

        # 카테고리 계층 생성
        # 대분류 -> 준분류 -> 소분류
        cls.large_category = QuestionCategory.objects.create(name="대분류")
        cls.medium_category = QuestionCategory.objects.create(name="중분류", parent=cls.large_category)
        cls.small_category = QuestionCategory.objects.create(name="소분류", parent=cls.medium_category)

        # 질문 생성 (각 계층별)
        cls.q_large = Question.objects.create(
            category=cls.large_category, author=cls.student_user, title="Q Large", content="Content"
        )
        cls.q_medium = Question.objects.create(
            category=cls.medium_category, author=cls.student_user, title="Q Medium", content="Content"
        )
        cls.q_small = Question.objects.create(
            category=cls.small_category, author=cls.student_user, title="Q Small", content="Content"
        )

        # URL
        cls.url = reverse("admin-qna-categories")

    # ==========================================================================
    # 성공 케이스
    # ==========================================================================
    def test_delete_large_category_success(self) -> None:
        """[200] 대분류 삭제 → 하위 모두 삭제, 질문은 '일반'으로 이동"""
        self.client.force_authenticate(user=self.admin_user)
        url = f"{self.url}/{self.large_category.id}"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 응답 검증
        self.assertEqual(response.data["category_id"], self.large_category.id)
        self.assertEqual(response.data["category_type"], "대분류")
        self.assertEqual(response.data["migrated_question_count"], 3)  # 대분류, 중분류, 소분류 모두 포함

        # DB 검증: 카테고리 삭제
        self.assertFalse(QuestionCategory.objects.filter(id=self.large_category.id).exists())
        self.assertFalse(QuestionCategory.objects.filter(id=self.medium_category.id).exists())
        self.assertFalse(QuestionCategory.objects.filter(id=self.small_category.id).exists())

        # DB 검증: 질문 이관
        default_category = QuestionCategory.objects.get(name=DEFAULT_CATEGORY)
        self.q_large.refresh_from_db()
        self.q_medium.refresh_from_db()
        self.q_small.refresh_from_db()
        self.assertEqual(self.q_large.category, default_category)
        self.assertEqual(self.q_medium.category, default_category)
        self.assertEqual(self.q_small.category, default_category)

    def test_delete_medium_category_success(self) -> None:
        """[200] 중분류 삭제 → 하위 모두 삭제, 질문은 '일반'으로 이동"""
        self.client.force_authenticate(user=self.admin_user)
        url = f"{self.url}/{self.medium_category.id}"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["category_type"], "중분류")
        self.assertEqual(response.data["migrated_question_count"], 2)  # 중분류, 소분류

        # DB 검증
        self.assertTrue(QuestionCategory.objects.filter(id=self.large_category.id).exists())  # 상위는 존재
        self.assertFalse(QuestionCategory.objects.filter(id=self.medium_category.id).exists())
        self.assertFalse(QuestionCategory.objects.filter(id=self.small_category.id).exists())

    # ==========================================================================
    # 실패 케이스
    # ==========================================================================
    def test_delete_category_unauthorized(self) -> None:
        """[401] 비로그인 접근"""
        url = f"{self.url}/{self.small_category.id}"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_category_forbidden_student(self) -> None:
        """[403] 일반 유저 접근"""
        self.client.force_authenticate(user=self.student_user)
        url = f"{self.url}/{self.small_category.id}"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_category_not_found(self) -> None:
        """[404] 존재하지 않는 카테고리"""
        self.client.force_authenticate(user=self.admin_user)
        url = f"{self.url}/9999"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_default_category_conflict(self) -> None:
        """[409] '일반' 카테고리 삭제 시도"""
        default_category = QuestionCategory.objects.create(name="일반 질문")
        self.client.force_authenticate(user=self.admin_user)
        url = f"{self.url}/{default_category.id}"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
