import logging
import sys
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail

from apps.qna.exceptions.base_e import QnaBaseException
from apps.qna.utils.constants import ErrorMessages

logger = logging.getLogger(__name__)


class QnaValidationMixin:
    """
    QnA 시리얼라이저 공통 예외 처리 Mixin
    """

    def is_valid(self, *, raise_exception: bool = False) -> bool:
        """DRF 내장 검증 로직 에러 캐치 및 커스텀 예외 반환"""
        try:
            return super().is_valid(raise_exception=raise_exception)  # type: ignore
        except serializers.ValidationError as e:
            is_testing = "test" in sys.argv or "pytest" in sys.modules or any("test" in arg for arg in sys.argv)

            # logger.warning을 통해 어떤 필드에서 검증이 실패했는지 기록
            if not is_testing:
                logger.warning(f"Validation Failed for {self.__class__.__name__}. " f"Detail: {e.detail}")

            extracted_msg, error_code = self._extract_error_info(e.detail)

            # 공통 에러 코드거나 필수 필드 누락인 경우 시리얼라이저의 default_error_message 사용
            generic_codes = {"required", "blank", "null", "invalid", "not_a_number", "invalid_choice", "max_length"}
            is_generic = error_code in generic_codes

            # 한국어/영어 필수 필드 메시지 명시적 체크
            is_required_msg = extracted_msg and ("필수 항목" in extracted_msg or "required" in extracted_msg.lower())

            if is_generic or is_required_msg or not extracted_msg:
                raw_default = getattr(self, "default_error_message", ErrorMessages.INVALID_REQUEST)
                extracted_msg = raw_default.value if isinstance(raw_default, Enum) else raw_default

            if raise_exception:
                raise QnaBaseException(detail=extracted_msg)
            return False

        except QnaBaseException:
            if raise_exception:
                raise
            return False

        except Exception as e:
            logger.error(
                f"데이터 검증 중 예상치 못한 시스템 에러 발생. "
                f"Serializer: {self.__class__.__name__}, Exception: {str(e)}",
                exc_info=True,
            )
            if raise_exception:
                raise QnaBaseException(detail=ErrorMessages.SYSTEM_ERROR)
            return False

    def _extract_error_info(self, detail: Union[Dict[str, Any], List[Any]]) -> tuple[Optional[str], Optional[str]]:
        """DRF의 중첩된 에러 구조에서 첫 번째 에러 메시지와 코드를 재귀적으로 추출"""
        if isinstance(detail, dict) and detail:
            # 딕셔너리의 첫 번째 키 값을 가져옴
            first_val = next(iter(detail.values()))
            return self._extract_error_info(first_val)

        if isinstance(detail, list) and detail:
            first_error = detail[0]
            if isinstance(first_error, (ErrorDetail, str)):
                msg = str(first_error)
                code = getattr(first_error, "code", "invalid")
                return msg, code
            return self._extract_error_info(first_error)

        return None, None
