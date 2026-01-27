from typing import Any

from rest_framework import serializers


class AdminExamDeploymentCourseSerializer(serializers.Serializer[Any]):
    """배포 상세 조회 코스 정보 스키마."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    tag = serializers.CharField()


class AdminExamDeploymentCohortSerializer(serializers.Serializer[Any]):
    """배포 상세 조회 기수 정보 스키마."""

    id = serializers.IntegerField()
    number = serializers.IntegerField()
    display = serializers.CharField()
    course = AdminExamDeploymentCourseSerializer()


class AdminExamDeploymentSubjectSerializer(serializers.Serializer[Any]):
    """배포 상세 조회 과목 정보 스키마."""

    id = serializers.IntegerField()
    name = serializers.CharField()


class AdminExamDeploymentQuestionSerializer(serializers.Serializer[Any]):
    """배포 상세 조회 문항 정보 스키마."""

    question_id = serializers.IntegerField()
    type = serializers.CharField()
    question = serializers.CharField()
    prompt = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    blank_count = serializers.IntegerField()
    options = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    point = serializers.IntegerField()


class AdminExamDeploymentExamSerializer(serializers.Serializer[Any]):
    """배포 상세 조회 시험 정보 스키마."""

    id = serializers.IntegerField()
    title = serializers.CharField()
    thumbnail_img_url = serializers.CharField()
    questions = AdminExamDeploymentQuestionSerializer(many=True)


class AdminExamDeploymentDetailResponseSerializer(serializers.Serializer[Any]):
    """어드민 쪽지시험 배포 상세 조회 응답 스키마."""

    id = serializers.IntegerField()
    exam_access_url = serializers.CharField()
    access_code = serializers.CharField()
    cohort = AdminExamDeploymentCohortSerializer()
    submit_count = serializers.IntegerField()
    not_submitted_count = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    close_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    exam = AdminExamDeploymentExamSerializer()
    subject = AdminExamDeploymentSubjectSerializer()
