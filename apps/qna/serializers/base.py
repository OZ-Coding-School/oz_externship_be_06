from typing import Any, cast
import logging

from rest_framework import serializers

from apps.qna.exceptions.question_exception import QuestionBaseException

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
            # Serializer에 정의된 커스텀 에러 메시지 사용
            error_message = getattr(self, "default_error_message", "유효하지 않은 요청입니다.")
            if raise_exception:
                raise QuestionBaseException(detail=error_message)
            return False
        except Exception as e:
            logger.error(
                f"데이터 검증 중 예상치 못한 서버 에러 발생. "
                f"Serializer: {self.__class__.__name__}, Exception: {str(e)}",
                exc_info=True,
            )

            if raise_exception:
                raise QuestionBaseException(detail=f"데이터 검증 중 오류 발생: {str(e)}")
            return False
