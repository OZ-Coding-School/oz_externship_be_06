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
    """
    Mock 데이터 생성 서비스
    """

    @classmethod
    def get_mock_question_list(cls) -> List[SafeMockObject]:
        """
        예시 데이터의 'results' 리스트에 있는 첫 번째 항목을 템플릿으로 사용하여
        10개의 Mock 질문 데이터를 생성
        """
        raw_results = SuccessResponseExamples.QUESTION_LIST.value.get("results", [])
        if not raw_results:
            return []

        # 템플릿으로 사용할 첫 번째 데이터 확보
        template_item = raw_results[0]
        mock_list = []

        for i in range(1, 11):
            # 템플릿을 복사하여 각 항목별로 고유한 값을 주입
            item = template_item.copy()
            item["id"] = i
            item["title"] = f"Mock 질문 제목 {i}"
            item["view_count"] = i * 15  # 조회수 가변 처리
            item["content_preview"] = f"{i}번째 미리보기. " + item.get("content_preview", "")
            # 객체 변환
            obj = cast(SafeMockObject, cls._dict_to_obj(item))
            # 데이터 정제(Hydration) 수행
            cls._hydrate_mock_object(obj, is_list=True)
            mock_list.append(obj)
        return mock_list

    def get_mock_category_tree(cls) -> List[SafeMockObject]:
        """
        [신규] 카테고리 트리 전용 Mock 데이터 생성
        명세서 예시 데이터를 SafeMockObject 트이 구조로 변환하여 반환합니다.
        """
        raw_categories = SuccessResponseExamples.QUESTION_CATEGORY_LIST.value.get("categories", [])
        # 리스트 내의 모든 dict를 재귀적으로 SafeMockObject로 변환
        return [cast(SafeMockObject, cls._dict_to_obj(cat)) for cat in raw_categories]

    @classmethod
    def get_mock_question_detail(cls, question_id: int) -> SafeMockObject:
        raw_data = SuccessResponseExamples.QUESTION_DETAIL.value.copy()
        raw_data["id"] = question_id

        obj = cast(SafeMockObject, cls._dict_to_obj(raw_data))
        cls._hydrate_mock_object(obj)

        return obj

    @classmethod
    def _hydrate_mock_object(cls, obj: SafeMockObject, is_list: bool = False) -> None:
        """Serializer 인터페이스에 맞게 Mock 객체 데이터를 재구성"""
        # Serializer의 parent 순회 로직 대응
        if hasattr(obj, "category") and obj.category:
            names = getattr(obj.category, "names", [])
            if names:
                parent_node = None
                for i, name_str in enumerate(names):
                    node_id = obj.category.id if i == len(names) - 1 else 0
                    current_node = SafeMockObject(id=node_id, name=name_str, parent=parent_node)
                    parent_node = current_node
                obj.category = parent_node
                # Serializer가 참조할 최종 계층 구조 객체로 교체
                obj.category = parent_node

        # Content & Thumbnail 처리
        content = getattr(obj, "content", None)
        # 목록 조회 시 content가 없고 content_preview만 있는 경우 대응
        if is_list and not content:
            content = getattr(obj, "content_preview", "Mock Content Body")
            setattr(obj, "content", content)

        if is_list:
            setattr(obj, "content_preview", ContentParser.extract_content_preview(content, 50))
            setattr(obj, "thumbnail_img_url", ContentParser.extract_thumbnail_img_url(content))

        #  ContentParser 대응
        current_content = getattr(obj, "content", None)
        if not current_content:
            # content가 없다면 content_preview를 원본 데이터로 주입하여 Parser가 동작하게 함
            preview_source = getattr(obj, "content_preview", "Mock Content Body")
            setattr(obj, "content", preview_source)

        # Author 이미지 및 필드 매핑
        if hasattr(obj, "author") and obj.author:
            author = obj.author
            img_url = getattr(author, "profile_image_url", None)
            if img_url and isinstance(img_url, str):
                wrapper = SafeMockObject(url=img_url)
                setattr(author, "profile_img_url", wrapper)
                setattr(author, "profile_image", wrapper)

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
