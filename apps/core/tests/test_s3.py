from io import BytesIO
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError
from django.test import TestCase, override_settings


@override_settings(
    AWS_S3_ACCESS_KEY_ID="test-key",
    AWS_S3_SECRET_ACCESS_KEY="test-secret",
    AWS_S3_REGION="ap-northeast-2",
    AWS_S3_BUCKET_NAME="test-bucket",
)
class S3ClientTests(TestCase):
    def setUp(self) -> None:
        self.mock_s3 = MagicMock()
        self.patcher = patch("boto3.client", return_value=self.mock_s3)
        self.patcher.start()

        from apps.core.utils.s3 import S3Client

        self.client = S3Client()

    def tearDown(self) -> None:
        self.patcher.stop()

    def test_upload_success(self) -> None:
        file = BytesIO(b"test content")
        file.name = "test.jpg"
        file.content_type = "image/jpeg"

        result = self.client.upload(file, path_prefix="images")

        self.mock_s3.upload_fileobj.assert_called_once()
        self.assertTrue(result.startswith("images/"))
        self.assertTrue(result.endswith(".jpg"))

    def test_upload_without_extension(self) -> None:
        file = BytesIO(b"test content")
        file.name = "noextension"

        result = self.client.upload(file)

        self.assertTrue(result.endswith(".bin"))

    def test_upload_with_extra_args(self) -> None:
        file = BytesIO(b"test content")
        file.name = "test.pdf"

        self.client.upload(file, extra_args={"ContentType": "application/pdf"})

        call_args = self.mock_s3.upload_fileobj.call_args
        self.assertEqual(call_args.kwargs["ExtraArgs"]["ContentType"], "application/pdf")

    def test_upload_client_error(self) -> None:
        file = BytesIO(b"test content")
        file.name = "test.jpg"

        self.mock_s3.upload_fileobj.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Internal Error"}},
            "upload_fileobj",
        )

        with self.assertRaises(ClientError):
            self.client.upload(file)

    def test_delete_success(self) -> None:
        self.client.delete("images/test.jpg")

        self.mock_s3.delete_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="images/test.jpg",
        )

    def test_delete_empty_key(self) -> None:
        self.client.delete("")

        self.mock_s3.delete_object.assert_not_called()

    def test_delete_client_error_logged(self) -> None:
        self.mock_s3.delete_object.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not Found"}},
            "delete_object",
        )

        self.client.delete("images/test.jpg")

    def test_delete_by_url(self) -> None:
        url = "https://test-bucket.s3.ap-northeast-2.amazonaws.com/images/test.jpg"

        self.client.delete_by_url(url)

        self.mock_s3.delete_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="images/test.jpg",
        )

    def test_build_url(self) -> None:
        result = self.client.build_url("images/test.jpg")

        self.assertEqual(
            result,
            "https://test-bucket.s3.ap-northeast-2.amazonaws.com/images/test.jpg",
        )

    def test_build_url_empty_key(self) -> None:
        result = self.client.build_url("")

        self.assertEqual(result, "")

    @override_settings(AWS_S3_CUSTOM_DOMAIN="cdn.example.com")
    def test_build_url_with_custom_domain(self) -> None:
        from apps.core.utils.s3 import S3Client

        client = S3Client()
        result = client.build_url("images/test.jpg")

        self.assertEqual(result, "https://cdn.example.com/images/test.jpg")

    def test_extract_key_from_url(self) -> None:
        url = "https://test-bucket.s3.ap-northeast-2.amazonaws.com/images/test.jpg"

        result = self.client.extract_key_from_url(url)

        self.assertEqual(result, "images/test.jpg")

    def test_extract_key_from_url_empty(self) -> None:
        result = self.client.extract_key_from_url("")

        self.assertEqual(result, "")

    def test_extract_key_from_url_invalid(self) -> None:
        result = self.client.extract_key_from_url("https://other-domain.com/test.jpg")

        self.assertEqual(result, "")

    @override_settings(AWS_S3_CUSTOM_DOMAIN="cdn.example.com")
    def test_extract_key_from_url_with_custom_domain(self) -> None:
        from apps.core.utils.s3 import S3Client

        client = S3Client()
        url = "https://cdn.example.com/images/test.jpg"

        result = client.extract_key_from_url(url)

        self.assertEqual(result, "images/test.jpg")

    def test_generate_presigned_url_success(self) -> None:
        self.mock_s3.generate_presigned_url.return_value = "https://presigned-url.com"

        result = self.client.generate_presigned_url("images/test.jpg", expires_in=3600)

        self.assertEqual(result, "https://presigned-url.com")
        self.mock_s3.generate_presigned_url.assert_called_once_with(
            ClientMethod="put_object",
            Params={"Bucket": "test-bucket", "Key": "images/test.jpg"},
            ExpiresIn=3600,
        )

    def test_generate_presigned_url_client_error(self) -> None:
        self.mock_s3.generate_presigned_url.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Internal Error"}},
            "generate_presigned_url",
        )

        with self.assertRaises(ClientError):
            self.client.generate_presigned_url("images/test.jpg")
