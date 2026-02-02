from enum import Enum
from typing import Dict, Optional

from botocore.exceptions import ClientError
from apps.qna.utils.s3_utils import S3Handler
from apps.qna.exceptions.base_e import QnaBaseException
from apps.qna.utils.constants import ErrorMessages
from rest_framework import status

class StorageTarget(Enum):
    """
    이미지 업로드 도메인 및 S3 경로 정의 Enum
    """

    QUESTION = ("question", "uploads/images/questions")
    ANSWER = ("answer", "uploads/images/answers")

    def __init__(self, domain: str, s3_path: str):
        self.domain = domain
        self.s3_path = s3_path


class PresignedUrlCommandService:
    """
    공통 이미지 업로드 URL 발급 서비스
    """

    @classmethod
    def get_presigned_url(cls, target: StorageTarget, file_name: str) -> Optional[Dict[str, str]]:
        """도메인(질문/답변)에 따라 경로를 결정하여 URL 발급"""
        s3_handler = S3Handler()

        if target is None:
            raise BaseException(
                ErrorMessages.INVALID_UPLOAD_DOMAIN,
                status.HTTP_400_BAD_REQUEST
            )

        try:
            result = s3_handler.generate_presigned_put_url(
                target.s3_path,
                file_name
            )
        except ClientError:
            raise BaseException(
                ErrorMessages.S3_CONNECTION_ERROR,
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if not result:
            raise BaseException(
                ErrorMessages.PRESIGNED_URL_GENERATION_ERROR,
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return result
