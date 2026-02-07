import json

from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.constants import ErrorMessages
from apps.qna.models import Answer, AnswerImage, Question, QuestionCategory

User = get_user_model()


class AnswerUpdateAPITest(APITestCase):
    """
    답변 수정 API (PUT) 테스트
    - 성공 케이스 (권한 있는 유저가 본인 답변 수정)
    - 실패 케이스
        - 401 Unauthorized: 로그인하지 않은 유저
        - 403 Forbidden: 다른 사람의 답변 수정 시도
        - 404 Not Found: 존재하지 않는 답변
        - 400 Bad Request: 필수 입력값(내용) 누락
    - 성능 테스트 (쿼리 수 검증)
    """

    def setUp(self) -> None:
        # self.client = APIClient()  # APITestCase provides this automatically

        # Users
        self.student = User.objects.create_user(
            email="student@ozcoding.com",
            password="password",
            nickname="학생",
            role="STUDENT",
            birthday="2000-01-01",
            is_active=True,
        )
        self.another_student = User.objects.create_user(
            email="another@ozcoding.com",
            password="password",
            nickname="다른학생",
            role="STUDENT",
            birthday="2000-01-01",
            is_active=True,
        )
        self.regular_user = User.objects.create_user(
            email="user@ozcoding.com",
            password="password",
            nickname="일반유저",
            role="USER",
            birthday="2000-01-01",
            is_active=True,
        )

        # Base Data
        self.category = QuestionCategory.objects.create(name="Python")
        self.question = Question.objects.create(
            author=self.student,
            category=self.category,
            title="질문입니다",
            content="내용",
        )
        self.answer = Answer.objects.create(
            question=self.question,
            author=self.student,
            content="원래 답변 내용",
        )
        AnswerImage.objects.create(
            answer=self.answer,
            img_url="https://example.com/old_img.png",
        )

        self.url = reverse("answer-update", kwargs={"answer_id": self.answer.id})

    def test_update_answer_success(self) -> None:
        """[성공] 본인이 작성한 답변 수정 성공 검증"""
        self.client.force_authenticate(user=self.student)

        data: dict[str, object] = {
            "content": "수정된 답변 내용입니다.",
            "image_urls": ["https://example.com/new_img1.png", "https://example.com/new_img2.png"],
        }

        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("answer_id", res_data)
        self.assertEqual(res_data["answer_id"], self.answer.id)
        self.assertIn("updated_at", res_data)

        # DB Verification
        self.answer.refresh_from_db()
        self.assertEqual(self.answer.content, "수정된 답변 내용입니다.")

        # 이미지 업데이트 확인
        images = AnswerImage.objects.filter(answer=self.answer)
        self.assertEqual(images.count(), 2)
        self.assertTrue(images.filter(img_url="https://example.com/new_img1.png").exists())
        self.assertTrue(images.filter(img_url="https://example.com/new_img2.png").exists())

    def test_update_answer_unauthorized(self) -> None:
        """[실패] 비로그인 상태로 요청 시 401 반환 검증"""
        data = {"content": "수정된 답변"}
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.UNAUTHORIZED_ANSWER_UPDATE.value)

    def test_update_answer_forbidden_not_owner(self) -> None:
        """[실패] 다른 사람의 답변 수정 시도 시 403 반환 검증"""
        self.client.force_authenticate(user=self.another_student)

        data = {"content": "수정 시도"}
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.FORBIDDEN_ANSWER_UPDATE.value)

    def test_update_answer_forbidden_role(self) -> None:
        """[실패] 허용되지 않은 Role(USER)로 요청 시 403 반환 검증"""
        # 일반 유저가 자신의 답변 만들기
        answer = Answer.objects.create(
            question=self.question,
            author=self.regular_user,
            content="일반 유저 답변",
        )
        url = reverse("answer-update", kwargs={"answer_id": answer.id})

        self.client.force_authenticate(user=self.regular_user)

        data = {"content": "수정 시도"}
        response = self.client.put(url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Permission check에서 막히므로 FORBIDDEN_ANSWER_UPDATE나 FORBIDDEN_ANSWER_CREATE 중 하나
        error_detail = response.json()["error_detail"]
        self.assertIn(
            error_detail, [ErrorMessages.FORBIDDEN_ANSWER_CREATE.value, ErrorMessages.FORBIDDEN_ANSWER_UPDATE.value]
        )

    def test_update_answer_not_found(self) -> None:
        """[실패] 존재하지 않는 답변 ID로 요청 시 404 반환 검증"""
        self.client.force_authenticate(user=self.student)

        invalid_url = reverse("answer-update", kwargs={"answer_id": 99999})
        data = {"content": "수정 시도"}
        response = self.client.put(invalid_url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.NOT_FOUND_ANSWER.value)

    def test_update_answer_invalid_input(self) -> None:
        """[실패] 필수 필드(content) 누락 시 400 반환 검증"""
        self.client.force_authenticate(user=self.student)

        data: dict[str, object] = {"image_urls": []}  # content missing
        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.INVALID_ANSWER_UPDATE.value)

    def test_update_answer_performance(self) -> None:
        """[성공] 답변 수정 시 쿼리 수 검증"""
        self.client.force_authenticate(user=self.student)
        data: dict[str, object] = {
            "content": "수정된 답변 내용",
            "image_urls": ["https://example.com/1.png", "https://example.com/2.png"],
        }

        # Query Expectation:
        # 1. Auth check (User) - cached or 1-2 queries
        # 2. Permission check (Role)
        # 3. Get Answer (select_for_update)
        # 4. Update Answer
        # 5. Delete old Images
        # 6. Bulk Create new Images
        # 7. Transaction overhead

        # Allow roughly 8-10 queries
        with CaptureQueriesContext(connection) as context:
            self.client.put(self.url, data=json.dumps(data), content_type="application/json", secure=False)

        self.assertLessEqual(len(context), 10, f"Too many queries: {len(context)}")

    def test_update_answer_remove_all_images(self) -> None:
        """[성공] 이미지를 모두 삭제하고 수정 성공 검증"""
        self.client.force_authenticate(user=self.student)

        data: dict[str, object] = {"content": "이미지 없는 답변", "image_urls": []}

        response = self.client.put(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 이미지가 모두 삭제되었는지 확인
        self.assertEqual(AnswerImage.objects.filter(answer=self.answer).count(), 0)
