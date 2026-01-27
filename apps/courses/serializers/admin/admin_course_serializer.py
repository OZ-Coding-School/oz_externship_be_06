from typing import Any

from rest_framework import serializers


# 어드민 과정 등록 요청
class CourseCreateRequestSerializer(serializers.Serializer[Any]):

    name = serializers.CharField(max_length=30)
    tag = serializers.CharField(max_length=3)
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)
    thumbnail_img_url = serializers.CharField(max_length=255, required=False, allow_blank=True)


# 어드민 과정 등록 응답
class CourseCreateResponseSerializer(serializers.Serializer[Any]):

    detail = serializers.CharField()
    id = serializers.IntegerField()


# 어드민 과정 수정 요청
class CourseUpdateRequestSerializer(serializers.Serializer[Any]):

    name = serializers.CharField(max_length=30, required=False)
    tag = serializers.CharField(max_length=3, required=False)
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)
    thumbnail_img_url = serializers.CharField(max_length=255, required=False, allow_blank=True)


# 어드민 과정 수정 응답
class CourseUpdateResponseSerializer(serializers.Serializer[Any]):

    id = serializers.IntegerField()
    name = serializers.CharField()
    tag = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    thumbnail_img_url = serializers.CharField(allow_null=True)
    updated_at = serializers.DateTimeField()
