from typing import Dict

from apps.qna.exceptions.base_e import QnaBaseException
from apps.qna.utils.s3_utils import S3Handler


class PresignedUrlCommandService:
    """
    공통 이미지 업로드 URL 발급 서비스
    (새로운 권한/자원을 생성하는 작업이므로 Command로 분류)
    """

    # 도메인별 S3 저장 경로 정의
    FOLDER_MAP = {
        "question": "uploads/images/questions",
        "answer": "uploads/images/answers",
    }

    @classmethod
    def get_presigned_url(cls, domain: str, file_name: str) -> Dict[str, str]:
        """
        도메인(질문/답변)에 따라 경로를 결정하여 URL 발급
        """
        folder_path = cls.FOLDER_MAP.get(domain)
        if not folder_path:
            raise QnaBaseException(detail="유효하지 않은 업로드 도메인입니다.")

        s3_handler = S3Handler()
        result = s3_handler.generate_presigned_put_url(folder_path, file_name)

        if not result:
            raise QnaBaseException(detail="이미지 서버 연결에 실패했습니다.")

        return result
