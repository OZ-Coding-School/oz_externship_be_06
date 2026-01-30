import logging
import uuid
from typing import Dict, Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


class S3Handler:
    """
    AWS S3 관련 저수준 작업을 처리하는 핸들러
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

    def generate_presigned_put_url(
        self, folder_path: str, file_name: str, expiration: int = 3600
    ) -> Optional[Dict[str, str]]:
        """파일 업로드를 위한 Presigned URL 발급"""
        # 파일명 충돌 방지를 위한 UUID 결합
        unique_file_name = f"{uuid.uuid4()}_{file_name}"
        object_key = f"{folder_path}/{unique_file_name}"

        try:
            presigned_url = self.s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_key,
                },
                ExpiresIn=expiration,
            )

            # 최종 접근 가능한 이미지 URL
            img_url = f"https://{self.bucket_name}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{object_key}"

            return {"presigned_url": presigned_url, "img_url": img_url, "key": object_key}
        except ClientError as e:
            logger.error(f"S3 Presigned URL 생성 실패: {str(e)}", exc_info=True)
            return None
