from __future__ import annotations

from rest_framework import serializers

from apps.qna.utils.model_types import User


# ==============================================================================
# Common Author Serializer
# ==============================================================================
class AuthorSerializer(serializers.ModelSerializer[User]):
    """
    작성자 정보 시리얼라이저 (질문, 답변, 댓글 공통)

    질문, 답변, 댓글 등 모든 컨텐츠의 작성자 정보를 표현할 때 사용합니다.
    """

    profile_image_url = serializers.ImageField(source="profile_img_url", use_url=True, help_text="프로필 이미지 URL")

    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image_url"]
