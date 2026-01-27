from rest_framework import serializers

from apps.courses.models import Course


# 과정 리스트 조회 응답
class CourseListResponseSerializer(serializers.ModelSerializer[Course]):

    class Meta:
        model = Course
        fields = ["id", "name", "tag", "thumbnail_img_url"]
