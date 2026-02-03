import unittest
from typing import Any, cast
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError

from apps.core.serializers.presigned_url import PresignedUrlRequestSerializer
from apps.core.services.presigned_url import PresignedUrlService
from apps.core.utils.s3_handler import S3Handler


class MockStorageTarget:
    """StorageTargetProtocol 규격을 만족하는 테스트용 가짜 객체"""

    domain = "test_domain"
    s3_path = "test/path"


class S3HandlerUnitTest(unittest.TestCase):
    """S3Handler 유틸리티 자체 로직 검증"""

    @patch("boto3.client")
    def setUp(self, mock_boto: MagicMock) -> None:
        self.mock_client = MagicMock()
        mock_boto.return_value = self.mock_client
        self.handler = S3Handler()

    def test_generate_presigned_url_success(self) -> None:
        """[성공] S3 Presigned URL 생성 및 데이터 구조 검증"""
        expected_url = "https://mock-s3-url.com/presigned"
        self.mock_client.generate_presigned_url.return_value = expected_url

        result = self.handler.generate_presigned_url("test_folder", "image.png")

        self.assertIsNotNone(result)
        if result is not None:
            self.assertEqual(result["presigned_url"], expected_url)
            self.assertIn("test_folder", result["key"])
            self.assertIn("image.png", result["key"])

    def test_generate_presigned_url_client_error(self) -> None:
        """[실패] Boto3 ClientError 발생 시 예외 전파 검증"""
        self.mock_client.generate_presigned_url.side_effect = ClientError(
            error_response={"Error": {"Code": "403", "Message": "Forbidden"}}, operation_name="GeneratePresignedUrl"
        )

        with self.assertRaises(ClientError):
            self.handler.generate_presigned_url("test_folder", "image.png")


class PresignedUrlRequestSerializerTest(unittest.TestCase):
    """시리얼라이저 확장자 검증 로직 테스트"""

    def test_validate_file_name_success(self) -> None:
        """[성공] 허용된 확장자 통과"""
        for name in ["test.jpg", "image.PNG", "graphic.gif"]:
            serializer = PresignedUrlRequestSerializer(data={"file_name": name})
            self.assertTrue(serializer.is_valid())

    def test_validate_file_name_fail(self) -> None:
        """[실패] 허용되지 않은 확장자 차단 (APIException 발생)"""
        serializer = PresignedUrlRequestSerializer(data={"file_name": "virus.exe"})
        with self.assertRaises(APIException) as cm:
            serializer.is_valid(raise_exception=True)

        detail = cast(dict[str, Any], cm.exception.detail)
        # 평탄화된 응답 구조 확인
        self.assertEqual(detail["error_detail"], "지원하지 않는 파일 형식입니다.")


class PresignedUrlCommandServiceTest(unittest.TestCase):
    """서비스 레이어 에러 래핑 테스트"""

    @patch("apps.core.services.presigned_url.S3Handler.generate_presigned_url")
    def test_get_presigned_url_s3_error_wrapping(self, mock_s3: MagicMock) -> None:
        """[실패] S3 장애(ClientError) 발생 시 500 APIException으로 변환"""
        mock_s3.side_effect = ClientError({"Error": {"Code": "500", "Message": "S3 Down"}}, "PutObject")

        with self.assertRaises(APIException) as cm:
            PresignedUrlService.get_presigned_url(MockStorageTarget(), "test.png")

        self.assertEqual(cm.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        detail = cast(dict[str, Any], cm.exception.detail)
        self.assertEqual(detail["error_detail"], "S3 연결 중 오류가 발생했습니다.")

    def test_get_presigned_url_target_none(self) -> None:
        """[실패] 타겟이 Protocol 규격에 맞지 않을 경우 400 ValidationError"""
        with self.assertRaises(ValidationError) as cm:
            # Protocol을 준수하지 않는 None 등을 주입 시 ValidationError(400) 발생
            PresignedUrlService.get_presigned_url(cast(Any, None), "test.png")

        self.assertEqual(cm.exception.status_code, status.HTTP_400_BAD_REQUEST)

        detail = cast(dict[str, Any], cm.exception.detail)
        self.assertEqual(detail["error_detail"], "유효하지 않은 업로드 도메인입니다.")
