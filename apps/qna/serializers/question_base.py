from typing import Any, cast

from apps.qna.exceptions.question_exception import QuestionBaseException


class QnAVersionedValidationMixin:
    """
    QnA 시리얼라이저에서 공통적으로 사용할 예외 처리 로직을 담은 Mixin class
    """

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:  # DRF의 내장 validate 로직에서 발생하는 에러 캐치
        try:
            validated_data = super().validate(attrs)  # type: ignore
            return cast(dict[str, Any], validated_data)
        except Exception as e:
            raise QuestionBaseException(detail=f"데이터 처리 중 오류가 발생했습니다: {str(e)}")
