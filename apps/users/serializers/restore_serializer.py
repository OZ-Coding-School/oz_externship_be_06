from typing import Any

from rest_framework import serializers


class RestoreSerializer(serializers.Serializer[Any]):
    email_token = serializers.CharField(allow_blank=False)


class RestoreSuccessSerializer(serializers.Serializer[Any]):
    detail = serializers.CharField()


class RestoreErrorDetailSerializer(serializers.Serializer[Any]):
    error_detail = serializers.CharField()
