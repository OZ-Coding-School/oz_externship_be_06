from typing import Any, cast

from rest_framework import serializers

from apps.qna.exceptions.question_exception import QuestionBaseException


class QnAVersionedValidationMixin:
    """
    QnA 시리얼라이저용 공통 예외 처리 Mixin
    """

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """DRF 내장 검증 로직 에러 캐치 및 커스텀 예외 반환"""
        try:
            validated_data = super().validate(attrs)  # type: ignore
            return cast(dict[str, Any], validated_data)
        except serializers.ValidationError as e:  # DRF 기본 ValidationError 발생 시
            raise QuestionBaseException(detail=e.detail)
        except Exception as e:  # 그 외 예상치 못한 에러
            raise QuestionBaseException(detail=f"데이터 처리 중 오류가 발생했습니다: {str(e)}")
