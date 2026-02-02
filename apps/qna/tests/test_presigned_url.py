import json
import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.utils.s3_utils import S3Handler
from apps.qna.utils.constants import ErrorMessages
from apps.qna.utils.model_types import User

UserModel = get_user_model()


class PresignedUrlAPITest(TestCase):
    """
    Presigned URL 발급 API 테스트
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
        self.q_url = reverse("question-presigned-url")
        self.a_url = reverse("answer-presigned-url")

    def _get_auth_header(self, user: User) -> Dict[str, Any]:
        refresh = RefreshToken.for_user(user)
        return {"Authorization": f"Bearer {str(refresh.access_token)}"}

    @patch("apps.qna.utils.s3_utils.S3Handler.generate_presigned_put_url")
    def test_question_presigned_url_success(self, mock_s3: Any) -> None:
        """[성공] 질문 이미지 업로드용 Presigned URL 발급"""
        mock_s3.return_value = {
            "presigned_url": "https://s3.url/path",
            "img_url": "https://s3.url/path",
            "key": "path",
        }

        data = {"file_name": "test.png"}

        response = self.client.put(
            self.q_url, data=json.dumps(data), content_type="application/json", headers=self._get_auth_header(self.user)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_s3.assert_called_once()

    @patch("apps.qna.utils.s3_utils.S3Handler.generate_presigned_put_url")
    def test_presigned_url_server_error(self, mock_s3: Any) -> None:
        """[실패] S3Handler가 None을 반환할 때(S3 장애 등) 500 에러 처리 검증"""
        mock_s3.return_value = None

        data = {"file_name": "test.png"}
        response = self.client.put(
            self.q_url, data=json.dumps(data), content_type="application/json", headers=self._get_auth_header(self.user)
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.S3_CONNECTION_ERROR.value)

    def test_presigned_url_unsupported_format(self) -> None:
        """[실패] 지원하지 않는 확장자 요청 시 400 에러"""
        data = {"file_name": "virus.exe"}
        response = self.client.put(
            self.q_url, data=json.dumps(data), content_type="application/json", headers=self._get_auth_header(self.user)
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.UNSUPPORTED_FILE_FORMAT.value)

    def test_presigned_url_unauthorized(self) -> None:
        """[실패] 미인증 유저 요청 시 401 에러"""
        data = {"file_name": "image.png"}
        # 인증 헤더 없이 요청
        response = self.client.put(self.q_url, data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class S3HandlerTest(unittest.TestCase):
    """
    S3Handler 유틸리티 자체 로직 검증
    """

    @patch("boto3.client")
    def setUp(self, mock_boto: MagicMock) -> None:
        self.mock_client = MagicMock()
        mock_boto.return_value = self.mock_client
        self.handler = S3Handler()

    def test_generate_presigned_put_url_success(self) -> None:
        """[성공] S3 Presigned URL 생성 및 반환 데이터 구조 검증"""
        # Given
        expected_url = "https://mock-s3-url.com/presigned"
        self.mock_client.generate_presigned_url.return_value = expected_url

        # When
        result = self.handler.generate_presigned_put_url("test_folder", "image.png")

        # Then
        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result["presigned_url"], expected_url)
            self.assertIn("test_folder", result["key"])
            self.assertIn("image.png", result["key"])
            self.assertIn("amazonaws.com", result["img_url"])

    @patch("apps.qna.utils.s3_utils.logger")
    def test_generate_presigned_put_url_client_error(self, mock_logger: MagicMock) -> None:
        """[실패] Boto3 ClientError 발생 시 None 반환 및 로깅 여부 검증"""
        # ClientError 강제 발생
        self.mock_client.generate_presigned_url.side_effect = ClientError(
            error_response={"Error": {"Code": "403", "Message": "Forbidden"}}, operation_name="GeneratePresignedUrl"
        )

        result = self.handler.generate_presigned_put_url("test_folder", "image.png")

        # 반환값이 None인지 확인
        self.assertIsNone(result)

        # 에러 로그가 실제로 기록되었는지 확인 (로직 검증)
        mock_logger.error.assert_called_once()
        # 호출된 인자 중 에러 메시지가 포함되어 있는지 확인 가능
        args, _ = mock_logger.error.call_args
        self.assertIn("S3 Presigned URL 생성 실패", args[0])
