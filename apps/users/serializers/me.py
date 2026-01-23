from rest_framework import serializers

from apps.users.models import User


class MeResponseSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    birthday = serializers.DateField(format="%Y-%m-%d", required=False, allow_null=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z", required=False, allow_null=True)
    gender = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "nickname",
            "name",
            "phone_number",
            "birthday",
            "gender",
            "profile_img_url",
            "created_at",
        )

    def get_gender(self, obj: User) -> str:
        # 기존 뷰 로직 그대로 반영
        return "M" if obj.gender == "MALE" else "F"
