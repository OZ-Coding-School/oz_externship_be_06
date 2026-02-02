from enum import Enum
from typing import Dict, Optional

from apps.qna.utils.s3_utils import S3Handler


class BucketPath(Enum):
    """
    이미지 업로드 도메인 및 S3 경로 정의 Enum
    """

    QUESTION = ("question", "uploads/images/questions")
    ANSWER = ("answer", "uploads/images/answers")

    def __init__(self, domain: str, s3_path: str):
        self.domain = domain
        self.s3_path = s3_path

    @classmethod
    def domain_to_s3path(cls, domain: str) -> Optional[str]:
        """입력받은 문자열 라벨에 해당하는 Enum 멤버 반환"""
        for target in cls:
            if target.domain == domain.lower():
                return target.s3_path


class PresignedUrlCommandService:
    """
    공통 이미지 업로드 URL 발급 서비스
    """

    @classmethod
    def get_presigned_url(cls, domain: str, file_name: str) -> Dict[str, str]:
        """도메인(질문/답변)에 따라 경로를 결정하여 URL 발급"""
        s3_path = BucketPath.domain_to_s3path(domain)
        s3_handler = S3Handler()
        result = s3_handler.generate_presigned_put_url(
            s3_path,
            file_name
        )

        return result