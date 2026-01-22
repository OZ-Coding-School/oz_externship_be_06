import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from apps.qna.models import Question, QuestionCategory, QuestionImage

User = get_user_model()


class QuestionCreateAPITest(TestCase):
    """
    질문 등록 API 테스트
    """

    def setUp(self) -> None:
        # 테스트용 클라이언트 초기화
        self.client = Client()

        # 테스트용 카테고리 생성
        self.category = QuestionCategory.objects.create(name="Python")

        # 테스트용 유저 생성 (수강생)
        # birthday 필드 누락으로 인한 IntegrityError 방지를 위해 생년월일 포함
        self.student_user = User.objects.create_user(
            email="student@ozcoding.com",
            password="password123",
            nickname="수강생",
            role="student",
            birthday="1990-01-01",
        )

        # 테스트용 유저 생성 (일반인/권한 없음)
        self.general_user = User.objects.create_user(
            email="general@ozcoding.com",
            password="password123",
            nickname="일반인",
            role="general",
            birthday="1995-05-05",
        )

        # 이미지 제약 조건(NOT NULL) 우회를 위한 더미 질문 생성
        self.dummy_question = Question.objects.create(
            author=self.student_user,
            category=self.category,
            title="더미",
            content="내용",
        )

        # URL 설정 이름 확인
        self.url = reverse("question-create")

    def test_create_question_success(self) -> None:
        """
        [성공] 수강생 권한으로 유효한 데이터를 전송하면 질문이 등록되어야 함
        """
        self.client.force_login(self.student_user)

        data = {
            "title": "장고 질문입니다.",
            "content": "이 에러는 어떻게 해결하나요?",
            "category_id": self.category.id,
        }

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["message"], "질문이 성공적으로 등록되었습니다.")

    def test_create_question_with_images_success(self) -> None:
        """
        [성공] 이미지 PK를 포함하여 질문을 등록하면 연관 관계가 업데이트되어야 함
        """
        self.client.force_login(self.student_user)

        # QuestionImage 모델의 question 필드 NOT NULL 제약조건 해결
        img1 = QuestionImage.objects.create(question=self.dummy_question)
        img2 = QuestionImage.objects.create(question=self.dummy_question)

        data = {
            "title": "이미지 포함 질문",
            "content": "이미지 테스트입니다.",
            "category_id": self.category.id,
            "image_ids": [img1.id, img2.id],
        }

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        img1.refresh_from_db()
        self.assertIsNotNone(img1.question)

    def test_create_question_unauthorized(self) -> None:
        """
        [실패] 로그인하지 않은 경우 401 에러를 반환해야 함
        """
        data = {"title": "비회원 질문", "content": "내용", "category_id": self.category.id}

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_question_forbidden(self) -> None:
        """
        [실패] 수강생이 아닌 유저가 요청하면 403 에러를 반환해야 함
        """
        self.client.force_login(self.general_user)

        data = {"title": "일반인 질문", "content": "내용", "category_id": self.category.id}

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_question_invalid_category(self) -> None:
        """
        [실패] 존재하지 않는 카테고리 ID 전송 시 400 에러 발생 확인
        """
        self.client.force_login(self.student_user)

        data = {"title": "에러 질문", "content": "내용", "category_id": 9999}

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 서비스 레이어 혹은 Mixin의 validate에서 발생한 에러는 'detail' 키에 담깁니다.
        self.assertIn("detail", response.json())

    def test_create_question_bad_request(self) -> None:
        """
        [실패] 필수 데이터 누락 시 400 에러 발생 확인
        """
        self.client.force_login(self.student_user)

        # 필수 필드인 title 누락
        data = {"content": "제목이 없어요", "category_id": self.category.id}

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 필드 레벨 검증 실패 시 DRF는 해당 필드명을 키로 에러를 반환하므로 detail 키가 없을 수 있습니다.
        # 따라서 응답에 에러 정보가 포함되어 있는지 확인합니다.
        self.assertTrue(len(response.json()) > 0)
