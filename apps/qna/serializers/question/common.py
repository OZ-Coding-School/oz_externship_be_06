from __future__ import annotations

from typing import Optional

from rest_framework import serializers

from apps.qna.models import QuestionCategory
from apps.qna.serializers.common import AuthorSerializer

# Re-export for backward compatibility
QuestionAuthorSerializer = AuthorSerializer


class QuestionCategoryListSerializer(serializers.ModelSerializer[QuestionCategory]):
    """
    질의응답 목록용 카테고리 시리얼라이저 (대 > 중 > 소 형태)
    """

    depth = serializers.SerializerMethodField()
    names = serializers.SerializerMethodField()

    class Meta:
        model = QuestionCategory
        fields = ["id", "depth", "names"]

    def get_depth(self, obj: Optional[QuestionCategory]) -> int:
        """모델에 필드가 없으므로 부모를 거슬러 올라가며 깊이를 계산"""
        depth = 0
        curr = getattr(obj, "parent", None)
        while curr:
            depth += 1
            curr = getattr(curr, "parent", None)
        return depth

    def get_names(self, obj: Optional[QuestionCategory]) -> list[str]:
        """부모 카테고리를 거슬러 올라가며 전체 경로 이름을 리스트로 생성"""
        names: list[str] = []
        curr: QuestionCategory | None = obj
        while curr:
            name = getattr(curr, "name", None)
            if name:
                names.append(name)
            curr = getattr(curr, "parent", None)
        return names[::-1]
