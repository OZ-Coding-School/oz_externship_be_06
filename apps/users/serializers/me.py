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
        return "M" if obj.gender == "MALE" else "F"


class MeUpdateRequestSerializer(serializers.Serializer):  # type: ignore[type-arg]
    nickname = serializers.CharField(max_length=10, required=False)
    name = serializers.CharField(max_length=30, required=False)
    birthday = serializers.DateField(required=False)
    gender = serializers.ChoiceField(choices=["M", "F"], required=False)


class MeUpdateResponseSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    birthday = serializers.DateField(format="%Y-%m-%d")
    gender = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "nickname",
            "name",
            "birthday",
            "gender",
            "phone_number",
            "updated_at",
        )

    def get_gender(self, obj: User) -> str:
        return "M" if obj.gender == "MALE" else "F"


class ProfileImageRequestSerializer(serializers.Serializer):  # type: ignore[type-arg]
    image = serializers.ImageField()


class ChangePhoneRequestSerializer(serializers.Serializer):  # type: ignore[type-arg]
    phone_verify_token = serializers.CharField()
