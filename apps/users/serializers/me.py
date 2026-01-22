from rest_framework import serializers


class MeResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    nickname = serializers.CharField()
    name = serializers.CharField()
    phone_number = serializers.CharField()
    birthday = serializers.DateField(allow_null=True)
    gender = serializers.CharField()
    profile_img_url = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.DateTimeField(allow_null=True)
