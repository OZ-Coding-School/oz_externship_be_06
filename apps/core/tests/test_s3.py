from typing import Any
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError
from django.test import TestCase, override_settings

from apps.core.utils.s3_handler import S3Handler


@override_settings(
    AWS_S3_ACCESS_KEY_ID="test-key",
    AWS_S3_SECRET_ACCESS_KEY="test-secret",
    AWS_S3_REGION="ap-northeast-2",
    AWS_S3_BUCKET_NAME="test-bucket",
)
class S3HandlerTests(TestCase):
    s3_handler: S3Handler
    mock_s3: Any

    def setUp(self) -> None:
        self.mock_s3 = MagicMock()
        self.patcher = patch("boto3.client", return_value=self.mock_s3)
        self.patcher.start()

        self.s3_handler = S3Handler()

    def tearDown(self) -> None:
        self.patcher.stop()

    def test_generate_presigned_url_success(self) -> None:
        self.mock_s3.generate_presigned_url.return_value = "https://presigned-url.com"

        result = self.s3_handler.generate_presigned_url("uploads/images", "test.png")

        self.assertIsNotNone(result)
        self.assertIn("presigned_url", result)
        self.assertIn("img_url", result)
        self.assertIn("key", result)
        self.assertEqual(result["presigned_url"], "https://presigned-url.com")
        self.assertTrue(result["key"].startswith("uploads/images/"))
        self.assertTrue(result["key"].endswith("_test.png"))

    def test_delete_success(self) -> None:
        self.s3_handler.delete("images/test.jpg")

        self.mock_s3.delete_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="images/test.jpg",
        )

    def test_delete_empty_key(self) -> None:
        self.s3_handler.delete("")

        self.mock_s3.delete_object.assert_not_called()

    def test_delete_client_error_logged(self) -> None:
        self.mock_s3.delete_object.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not Found"}},
            "delete_object",
        )

        self.s3_handler.delete("images/test.jpg")

    def test_delete_by_url(self) -> None:
        url = "https://test-bucket.s3.ap-northeast-2.amazonaws.com/images/test.jpg"

        self.s3_handler.delete_by_url(url)

        self.mock_s3.delete_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="images/test.jpg",
        )

    def test_build_url(self) -> None:
        result = self.s3_handler.build_url("images/test.jpg")

        self.assertEqual(
            result,
            "https://test-bucket.s3.ap-northeast-2.amazonaws.com/images/test.jpg",
        )

    def test_build_url_empty_key(self) -> None:
        result = self.s3_handler.build_url("")

        self.assertEqual(result, "")

    @override_settings(AWS_S3_CUSTOM_DOMAIN="cdn.example.com")
    def test_build_url_with_custom_domain(self) -> None:
        handler = S3Handler()
        result = handler.build_url("images/test.jpg")

        self.assertEqual(result, "https://cdn.example.com/images/test.jpg")

    def test_extract_key_from_url(self) -> None:
        url = "https://test-bucket.s3.ap-northeast-2.amazonaws.com/images/test.jpg"

        result = self.s3_handler.extract_key_from_url(url)

        self.assertEqual(result, "images/test.jpg")

    def test_extract_key_from_url_empty(self) -> None:
        result = self.s3_handler.extract_key_from_url("")

        self.assertEqual(result, "")

    def test_extract_key_from_url_invalid(self) -> None:
        result = self.s3_handler.extract_key_from_url("https://other-domain.com/test.jpg")

        self.assertEqual(result, "")

    @override_settings(AWS_S3_CUSTOM_DOMAIN="cdn.example.com")
    def test_extract_key_from_url_with_custom_domain(self) -> None:
        handler = S3Handler()
        url = "https://cdn.example.com/images/test.jpg"

        result = handler.extract_key_from_url(url)

        self.assertEqual(result, "images/test.jpg")
