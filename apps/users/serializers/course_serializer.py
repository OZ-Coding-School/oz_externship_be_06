from typing import Any

from rest_framework import serializers


# 기수 정보
class CohortInfoSerializer(serializers.Serializer[Any]):

    id = serializers.IntegerField()
    number = serializers.IntegerField()
    start_date = serializers.DateField(format="%Y-%m-%d")
    end_date = serializers.DateField(format="%Y-%m-%d")


# 과정 정보
class CourseInfoSerializer(serializers.Serializer[Any]):

    id = serializers.IntegerField()
    name = serializers.CharField()


# 과정 상세 정보
class CourseDetailInfoSerializer(serializers.Serializer[Any]):

    id = serializers.IntegerField()
    name = serializers.CharField()
    tag = serializers.CharField()
    thumbnail_img_url = serializers.CharField(allow_null=True)


# 수강신청 가능한 과정/기수
class AvailableCourseResponseSerializer(serializers.Serializer[Any]):

    course = CourseInfoSerializer()
    cohorts = CohortInfoSerializer(many=True)


# 내 수강 목록 응답
class EnrolledCourseResponseSerializer(serializers.Serializer[Any]):

    cohort = CohortInfoSerializer()
    course = CourseDetailInfoSerializer()
