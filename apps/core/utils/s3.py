import logging
import uuid
from typing import Any

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from mypy_boto3_s3 import S3Client as BotoS3Client

logger = logging.getLogger(__name__)

# !!!!!!!!!!!!!!! 환경변수 추가 안함 !!!!!!!!!!!!!!!!!!!!!!!!


class S3Client:
    def __init__(self) -> None:
        self.s3: BotoS3Client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION,
        )
        self.bucket_name: str = settings.AWS_S3_BUCKET_NAME

    def upload(
        self,
        file: Any,
        path_prefix: str = "",
        extra_args: dict[str, Any] | None = None,
    ) -> str:

        original_name = getattr(file, "name", "unknown_file")
        ext = original_name.split(".")[-1] if "." in original_name else "bin"

        file_name = f"{uuid.uuid4()}.{ext}"

        clean_prefix = path_prefix.strip("/")
        key = f"{clean_prefix}/{file_name}" if clean_prefix else file_name

        upload_params: dict[str, Any] = extra_args.copy() if extra_args else {}

        if "ContentType" not in upload_params:
            content_type = getattr(file, "content_type", None)
            if content_type:
                upload_params["ContentType"] = content_type

        try:
            self.s3.upload_fileobj(file, self.bucket_name, key, ExtraArgs=upload_params)
            return key
        except ClientError as e:
            logger.error(f"S3 Upload Error: {e}", exc_info=True)
            raise

    # S3에서 파일 삭제"
    def delete(self, key: str) -> None:
        if not key:
            return
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
        except ClientError as e:
            logger.warning(f"S3 Delete Failed (Key: {key}): {e}", exc_info=True)

    # S3 URL로 파일 삭제
    def delete_by_url(self, url: str) -> None:
        key = self.extract_key_from_url(url)
        if key:
            self.delete(key)

    # S3 key로 URL 생성
    def build_url(self, key: str) -> str:
        if not key:
            return ""

        custom_domain = getattr(settings, "AWS_S3_CUSTOM_DOMAIN", None)

        if custom_domain:
            domain = custom_domain
        else:
            domain = f"{self.bucket_name}.s3.{settings.AWS_S3_REGION}.amazonaws.com"

        return f"https://{domain.rstrip('/')}/{key.lstrip('/')}"

    # S3 URL에서 key 추출
    def extract_key_from_url(self, url: str) -> str:
        if not url:
            return ""

        custom_domain = getattr(settings, "AWS_S3_CUSTOM_DOMAIN", None)

        if custom_domain:
            prefix = f"https://{custom_domain}/"
        else:
            prefix = f"https://{self.bucket_name}.s3.{settings.AWS_S3_REGION}.amazonaws.com/"

        if url.startswith(prefix):
            return url.replace(prefix, "")
        return ""

    # Presigned URL 생성 (프론트에서 직접 업로드용)
    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            return self.s3.generate_presigned_url(
                ClientMethod="put_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL (Key: {key}): {e}", exc_info=True)
            raise
