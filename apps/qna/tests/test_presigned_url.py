import json
from typing import Any
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.tests.factories import create_student_user
from apps.qna.views.presigned_url_views import StorageTarget
from apps.users.models import User


class PresignedUrlAPITest(APITestCase):
    """
    질문/답변 도메인별 API 연결 검증
    - 성공 케이스 (QUSTION, ANSWER 도메인)
    """

    student_user: User
    question_url: str
    answer_url: str

    @classmethod
    def setUpTestData(cls) -> None:
        # 테스트용 유저
        cls.student_user = create_student_user()

        # URL
        cls.question_url = reverse("question-presigned-url")
        cls.answer_url = reverse("answer-presigned-url")

    # ==========================================================================
    # 성공 케이스
    # ==========================================================================
    @patch("apps.core.services.presigned_url.S3Handler.generate_presigned_url")
    def test_question_endpoint_wiring(self, mock_s3: Any) -> None:
        """[200] 질문 도메인이 QUESTION 경로 사용"""
        mock_s3.return_value = {"presigned_url": "url", "img_url": "url", "key": "key"}

        self.client.force_authenticate(user=self.student_user)
        response = self.client.put(
            self.question_url,
            data=json.dumps({"file_name": "test.png"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 서비스 호출 시 QUESTION 타겟의 경로가 전달되었는지 검증
        args, _ = mock_s3.call_args
        self.assertEqual(args[0], StorageTarget.QUESTION.s3_path)

    @patch("apps.core.services.presigned_url.S3Handler.generate_presigned_url")
    def test_answer_endpoint_wiring(self, mock_s3: Any) -> None:
        """[200] 질문 도메인이 ANSWER 경로 사용"""
        mock_s3.return_value = {"presigned_url": "url", "img_url": "url", "key": "key"}

        self.client.force_authenticate(user=self.student_user)
        response = self.client.put(
            self.answer_url,
            data=json.dumps({"file_name": "test.png"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 서비스 호출 시 QUESTION 타겟의 경로가 전달되었는지 검증
        args, _ = mock_s3.call_args
        self.assertEqual(args[0], StorageTarget.ANSWER.s3_path)
