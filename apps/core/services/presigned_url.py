import logging
from typing import Dict, Protocol, runtime_checkable

from botocore.exceptions import ClientError
from rest_framework import status

from apps.core.exceptions.base import CoreBaseException
from apps.core.utils.s3_handler import S3Handler

logger = logging.getLogger("django")


@runtime_checkable
class StorageTargetProtocol(Protocol):
    """
    S3 업로드 타겟의 추상 규격
    """

    domain: str
    s3_path: str


class PresignedUrlService:
    """
    공통 이미지 업로드 URL 발급 서비스
    """

    @classmethod
    def get_presigned_url(cls, target: StorageTargetProtocol, file_name: str) -> Dict[str, str]:
        """도메인(질문/답변)에 따라 경로를 결정하여 URL 발급"""
        if not isinstance(target, StorageTargetProtocol):
            logger.error(f"[INVALID_TARGET] Target {type(target)} does not implement StorageTargetProtocol")
            raise CoreBaseException("유효하지 않은 업로드 도메인입니다.", status.HTTP_400_BAD_REQUEST)

        s3_handler = S3Handler()

        try:
            result = s3_handler.generate_presigned_url(target.s3_path, file_name)
        except ClientError as e:
            logger.error(
                f"[S3_API_FAILURE] Target: {target.domain} | File: {file_name} | Reason: {str(e)}", exc_info=True
            )
            raise CoreBaseException("S3 연결 중 오류가 발생했습니다.", status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not result:
            logger.error(f"[S3_LOGIC_ERROR] Presigned URL result is empty for {file_name}")
            raise CoreBaseException("URL 생성에 실패했습니다.", status.HTTP_500_INTERNAL_SERVER_ERROR)
        return result
