import logging
import mimetypes
import uuid
from typing import Dict

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


class S3Handler:
    """
    AWS S3 관련 작업을 처리하는 핸들러
    - Presigned URL 발급
    - 파일 삭제
    - URL/Key 변환
    """

    def __init__(self) -> None:
        # S3 Signature 버전 v4 강제 및 리전 설정
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION,
            config=Config(signature_version="s3v4"),
        )
        self.bucket_name = settings.AWS_S3_BUCKET_NAME

    def generate_presigned_url(self, folder_path: str, file_name: str, expiration: int = 3600) -> Dict[str, str]:
        """파일 업로드를 위한 Presigned URL 발급"""
        # 파일명 충돌 방지를 위한 UUID 결합
        unique_file_name = f"{uuid.uuid4()}_{file_name}"
        object_key = f"{folder_path}/{unique_file_name}"

        # 파일명을 통한 MIME 타입 추론
        content_type, _ = mimetypes.guess_type(file_name)
        # 추론 불가 시 기본값 설정
        if not content_type:
            content_type = "application/octet-stream"

        presigned_url = self.s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=expiration,
        )

        # 최종 접근 가능한 이미지 URL
        img_url = self.build_url(object_key)

        return {"presigned_url": presigned_url, "img_url": img_url, "key": object_key}

    def delete(self, key: str) -> None:
        if not key:
            return
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
        except ClientError as e:
            logger.warning(f"S3 Delete Failed (Key: {key}): {e}", exc_info=True)

    def delete_by_url(self, url: str) -> None:
        key = self.extract_key_from_url(url)
        if key:
            self.delete(key)

    def build_url(self, key: str) -> str:
        if not key:
            return ""

        custom_domain = getattr(settings, "AWS_S3_CUSTOM_DOMAIN", None)

        if custom_domain:
            domain = custom_domain
        else:
            domain = f"{self.bucket_name}.s3.{settings.AWS_S3_REGION}.amazonaws.com"

        return f"https://{domain.rstrip('/')}/{key.lstrip('/')}"

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
