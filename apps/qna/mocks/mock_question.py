from types import SimpleNamespace
from typing import Any, List, cast

from apps.qna.docs.api_response_examples import SuccessResponseExamples
from apps.qna.utils.content_parser import ContentParser


class SafeMockObject(SimpleNamespace):
    """
    Serializer의 속성 접근을 안전하게 방어하고 Django 모델처럼 동작하는 Mock 객체
    """

    def __getattr__(self, name: str) -> Any:
        # Django 모델 인스턴스처럼 존재하지 않는 필드 접근 시 None 반환
        return None


class QuestionMockService:

    @classmethod
    def get_mock_category_tree(cls) -> List[SafeMockObject]:
        """
        [신규] 카테고리 트리 전용 Mock 데이터 생성
        명세서 예시 데이터를 SafeMockObject 트이 구조로 변환하여 반환합니다.
        """
        raw_categories = SuccessResponseExamples.QUESTION_CATEGORY_LIST.value.get("categories", [])
        # 리스트 내의 모든 dict를 재귀적으로 SafeMockObject로 변환
        return [cast(SafeMockObject, cls._dict_to_obj(cat)) for cat in raw_categories]

    @staticmethod
    def _dict_to_obj(data: Any) -> Any:
        """딕셔너리를 재귀적으로 SafeMockObject로 변환하여 속성 접근(.)이 가능하게 함"""
        if isinstance(data, list):
            return [QuestionMockService._dict_to_obj(v) for v in data]
        if isinstance(data, dict):
            obj = SafeMockObject()
            for k, v in data.items():
                setattr(obj, k, QuestionMockService._dict_to_obj(v))
            return obj
        return data
