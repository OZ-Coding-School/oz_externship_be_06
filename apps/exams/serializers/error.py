from rest_framework import serializers


class ErrorDetailSerializer(serializers.Serializer):
    error_detail = serializers.CharField(
        help_text="에러 상세 메시지"
    )