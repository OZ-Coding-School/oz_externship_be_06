import json
from typing import Any, Dict
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.services.command import StorageTarget
from apps.qna.utils.model_types import User

UserModel = get_user_model()


class PresignedUrlAPITest(TestCase):
    """
    질문/답변 도메인별 API 연결 검증
    - 성공 케이스 (QUSTION, ANSWER 도메인)
    """

    def setUp(self) -> None:
        self.client = Client()
        self.user = UserModel.objects.create_user(
            email="test@ozcoding.com",
            password="password",
            nickname="테스터",
            role="STUDENT",
            birthday="2000-01-01",
            is_active=True,
        )
        self.question_url = reverse("question-presigned-url")
        self.answer_url = reverse("answer-presigned-url")

    def _get_auth_header(self, user: User) -> Dict[str, Any]:
        refresh = RefreshToken.for_user(user)
        return {"Authorization": f"Bearer {str(refresh.access_token)}"}

    @patch("apps.core.services.command.S3Handler.generate_presigned_put_url")
    def test_question_endpoint_wiring(self, mock_s3: Any) -> None:
        """[성공] 질문 도메인이 QUESTION 경로를 사용하는지 확인"""
        mock_s3.return_value = {"presigned_url": "url", "img_url": "url", "key": "key"}

        response = self.client.put(
            self.question_url,
            data=json.dumps({"file_name": "test.png"}),
            content_type="application/json",
            headers=self._get_auth_header(self.user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 서비스 호출 시 QUESTION 타겟의 경로가 전달되었는지 검증
        args, _ = mock_s3.call_args
        self.assertEqual(args[0], StorageTarget.QUESTION.s3_path)

    @patch("apps.core.services.command.S3Handler.generate_presigned_put_url")
    def test_answer_endpoint_wiring(self, mock_s3: Any) -> None:
        """[성공] 질문 도메인이 ANSWER 경로를 사용하는지 확인"""
        mock_s3.return_value = {"presigned_url": "url", "img_url": "url", "key": "key"}

        response = self.client.put(
            self.answer_url,
            data=json.dumps({"file_name": "test.png"}),
            content_type="application/json",
            headers=self._get_auth_header(self.user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 서비스 호출 시 QUESTION 타겟의 경로가 전달되었는지 검증
        args, _ = mock_s3.call_args
        self.assertEqual(args[0], StorageTarget.ANSWER.s3_path)
