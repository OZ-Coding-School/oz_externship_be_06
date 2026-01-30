from rest_framework import serializers

from apps.qna.models import QuestionCategory
from apps.qna.utils.model_types import User


class QuestionCategoryListSerializer(serializers.ModelSerializer[QuestionCategory]):
    """
    질의응답 목록용 카테고리 시리얼라이저 (대 > 중 > 소 형태)
    """

    depth = serializers.SerializerMethodField()
    names = serializers.SerializerMethodField()

    class Meta:
        model = QuestionCategory
        fields = ["id", "depth", "names"]

    def get_depth(self, obj: QuestionCategory) -> int:
        """모델에 필드가 없으므로 부모를 거슬러 올라가며 깊이를 계산"""
        depth = 0
        curr = obj.parent
        while curr:
            depth += 1
            curr = curr.parent
        return depth

    def get_names(self, obj: QuestionCategory) -> list[str]:
        """부모 카테고리를 거슬러 올라가며 전체 경로 이름을 리스트로 생성"""
        names: list[str] = []
        curr: QuestionCategory | None = obj
        while curr:
            names.insert(0, curr.name)
            curr = curr.parent
        return names


class QuestionAuthorSerializer(serializers.ModelSerializer[User]):
    """
    질문 작성자 정보 시리얼라이저
    """

    profile_image_url = serializers.ImageField(source="profile_img_url", use_url=True)

    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image_url"]
