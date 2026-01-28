from typing import Any

from rest_framework import serializers


class AdminExamSubmissionListResponseSerializer(serializers.Serializer[Any]):
    """어드민 쪽지시험 응시 내역 목록 조회 응답 스키마."""

    submission_id = serializers.IntegerField(source="id")
    nickname = serializers.CharField(source="submitter.nickname")
    name = serializers.CharField(source="submitter.name")
    course_name = serializers.CharField(source="deployment.cohort.course.name")
    cohort_number = serializers.IntegerField(source="deployment.cohort.number")
    exam_title = serializers.CharField(source="deployment.exam.title")
    subject_name = serializers.CharField(source="deployment.exam.subject.title")
    score = serializers.IntegerField()
    cheating_count = serializers.IntegerField()
    started_at = serializers.DateTimeField()
    finished_at = serializers.DateTimeField(source="created_at")
