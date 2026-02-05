from typing import Any

from rest_framework import serializers

from apps.courses.models import Subject


class SubjectListSerializer(serializers.ModelSerializer[Subject]):
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ["id", "course_id", "title", "status", "thumbnail_img_url"]

    def get_status(self, obj: Subject) -> str:
        return "activated" if obj.status else "deactivated"


class SubjectScatterSerializer(serializers.Serializer):  # type: ignore[type-arg]
    time = serializers.FloatField()
    score = serializers.IntegerField()


# 과목생성요청
class SubjectCreateRequestSerializer(serializers.Serializer[Any]):

    course_id = serializers.IntegerField(required=True, help_text="과정 ID")
    title = serializers.CharField(required=True, max_length=30, help_text="과목명")
    number_of_days = serializers.IntegerField(required=True, min_value=1, help_text="일수")
    number_of_hours = serializers.IntegerField(required=True, min_value=1, help_text="시간")
    thumbnail_img_url = serializers.CharField(
        required=False, allow_blank=True, max_length=255, help_text="썸네일 이미지 URL"
    )


# 과목 생성 응답
class SubjectCreateResponseSerializer(serializers.ModelSerializer[Subject]):

    course_id = serializers.IntegerField(source="course.id", read_only=True)

    class Meta:
        model = Subject
        fields = ["id", "course_id", "title", "number_of_days", "number_of_hours", "thumbnail_img_url", "status"]
