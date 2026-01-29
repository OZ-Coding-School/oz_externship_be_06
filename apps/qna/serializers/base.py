import logging

from rest_framework import serializers

from apps.qna.exceptions.base_e import QnaBaseException
from apps.qna.utils.constants import ErrorMessages

logger = logging.getLogger(__name__)


class QnaValidationMixin:
    """
    QnA 시리얼라이저용 공통 예외 처리 Mixin
    """

    def is_valid(self, *, raise_exception: bool = False) -> bool:
        """DRF 내장 검증 로직 에러 캐치 및 커스텀 예외 반환"""
        try:
            return super().is_valid(raise_exception=raise_exception)  # type: ignore
        except serializers.ValidationError:
            error_message = getattr(self, "default_error_message", ErrorMessages.INVALID_REQUEST)
            if raise_exception:
                raise QnaBaseException(detail=error_message)
            return False

        except Exception as e:
            logger.error(
                f"데이터 검증 중 예상치 못한 에러 발생. " f"Serializer: {self.__class__.__name__}, Exception: {str(e)}",
                exc_info=True,
            )
            if raise_exception:
                raise QnaBaseException(detail=f"데이터 검증 중 오류 발생: {str(e)}")
            return False
