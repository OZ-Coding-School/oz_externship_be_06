from typing import Any, cast

from rest_framework import serializers

from apps.qna.exceptions.question_exception import QuestionBaseException


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
            if raise_exception:
                raise QuestionBaseException(detail=f"데이터 검증 중 오류 발생: {str(e)}")
            return False
