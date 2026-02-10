from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.models import Question, QuestionCategory, QuestionImage
from apps.users.models import User


class QuestionUpdateAPITestResult(APITestCase):
    """
    질문 수정 API (PUT) 테스트
    - 성공 케이스
        - 200 OK: 질문 수정 성공
    - 실패 케이스
        - 400 Bad Request: 필수 필드 누락
        - 400 Bad Request: 잘못된 데이터 타입
        - 401 Unauthorized: 인증되지 않은 사용자
        - 403 Forbidden: 본인이 작성한 질문이 아닌 경우
        - 404 Not Found: 존재하지 않는 질문
        - 404 Not Found: 존재하지 않는 카테고리
    """

    user: User
    other_user: User
    parent_category: QuestionCategory
    category: QuestionCategory
    other_category: QuestionCategory
    question: Question
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        # 테스트용 유저 - 학생
        cls.user = User.objects.create_user(
            email="test@example.com",
            password="password",
            name="Test User",
            nickname="test",
            role="STUDENT",
            phone_number="01012345678",
            gender="MALE",
            birthday="2000-01-01",
        )
        # 테스트용 유저 - 다른 학생
        cls.other_user = User.objects.create_user(
            email="other@example.com",
            password="password",
            name="Other User",
            nickname="other",
            role="STUDENT",
            phone_number="01087654321",
            gender="FEMALE",
            birthday="2000-01-01",
        )

        # 카테고리 생성 (depth=1을 만들기 위해 부모 카테고리 생성)
        cls.parent_category = QuestionCategory.objects.create(name="Programming")
        cls.category = QuestionCategory.objects.create(name="Python", parent=cls.parent_category)
        cls.other_category = QuestionCategory.objects.create(name="Django", parent=cls.parent_category)

        # 질문 생성
        cls.question = Question.objects.create(
            author=cls.user, title="Old Title", content="Old Content", category=cls.category
        )

        # URL
        cls.url = f"/api/v1/qna/questions/{cls.question.id}"

    def test_update_question_success(self) -> None:
        """[성공] 질문 수정 성공 테스트"""
        self.client.force_authenticate(user=self.user)

        data = {
            "title": "New Title",
            "content": "New Content ![image](http://example.com/image1.jpg) with image url",
            "category_id": self.other_category.id,
        }

        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.question.refresh_from_db()
        self.assertEqual(self.question.title, "New Title")
        self.assertEqual(self.question.content, "New Content ![image](http://example.com/image1.jpg) with image url")
        self.assertEqual(self.question.category, self.other_category)
        self.assertEqual(QuestionImage.objects.count(), 1)
        first_image = QuestionImage.objects.first()
        assert first_image is not None
        self.assertEqual(first_image.img_url, "http://example.com/image1.jpg")

    def test_update_question_missing_title(self) -> None:
        """[실패] 필수 필드 누락 시 400 에러 테스트 (title 누락)"""
        self.client.force_authenticate(user=self.user)

        data = {"content": "New Content", "category_id": self.category.id}  # title 누락

        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    def test_update_question_missing_content(self) -> None:
        """[실패] 필수 필드 누락 시 400 에러 테스트 (content 누락)"""
        self.client.force_authenticate(user=self.user)

        data = {"title": "New Title", "category_id": self.category.id}  # content 누락

        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    def test_update_question_missing_category_id(self) -> None:
        """[실패] 필수 필드 누락 시 400 에러 테스트 (category_id 누락)"""
        self.client.force_authenticate(user=self.user)

        data = {"title": "New Title", "content": "New Content"}  # category_id 누락

        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    def test_update_question_invalid_category_id_type(self) -> None:
        """[실패] 잘못된 데이터 타입 시 400 에러 테스트 (category_id가 문자열)"""
        self.client.force_authenticate(user=self.user)

        data = {"title": "New Title", "content": "New Content", "category_id": "invalid"}  # 문자열

        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    def test_update_question_unauthorized(self) -> None:
        """[실패] 인증되지 않은 사용자 401 에러 테스트"""
        data = {"title": "New Title", "content": "New Content", "category_id": self.category.id}

        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_question_forbidden_not_author(self) -> None:
        """[실패] 본인 질문이 아닌 경우 403 에러 테스트"""
        self.client.force_authenticate(user=self.other_user)

        data = {"title": "New Title", "content": "New Content", "category_id": self.category.id}

        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_question_not_found(self) -> None:
        """[실패] 존재하지 않는 질문 수정 시 404 에러 테스트"""
        self.client.force_authenticate(user=self.user)

        url = "/api/v1/qna/questions/99999"
        data = {"title": "New Title", "content": "New Content", "category_id": self.category.id}

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_question_invalid_category(self) -> None:
        """[실패] 유효하지 않은 데이터로 수정 시 404 에러 테스트 (카테고리 없음)"""
        self.client.force_authenticate(user=self.user)

        data = {"title": "New Title", "content": "New Content", "category_id": 99999}  # 존재하지 않는 카테고리

        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
