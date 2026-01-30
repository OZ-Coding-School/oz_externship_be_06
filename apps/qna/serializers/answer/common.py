from rest_framework import serializers

from apps.qna.utils.model_types import User


class AnswerAuthorSerializer(serializers.Serializer[User]):
    """
    답변 및 댓글 작성자 정보 시리얼라이저
    """

    id = serializers.IntegerField(help_text="작성자 ID")
    nickname = serializers.CharField(help_text="작성자 닉네임")
    profile_image_url = serializers.ImageField(source="profile_img_url", use_url=True, help_text="프로필 이미지 URL")
