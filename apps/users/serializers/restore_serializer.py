from typing import Any

from rest_framework import serializers


class RestoreSerializer(serializers.Serializer[dict[str, Any]]):
    email_token = serializers.CharField(allow_blank=False)


class RestoreSuccessSerializer(serializers.Serializer[dict[str, Any]]):
    detail = serializers.CharField()


class RestoreErrorDetailSerializer(serializers.Serializer[dict[str, Any]]):
    error_detail = serializers.CharField()
