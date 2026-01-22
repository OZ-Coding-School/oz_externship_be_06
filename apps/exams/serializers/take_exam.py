from __future__ import annotations

from rest_framework import serializers


class TakeExamRequestSerializer(serializers.Serializer):
    access_code = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=64,
        help_text="참가코드(Base62 인코딩된 값)",
    )


class TakeExamResponseSerializer(serializers.Serializer):
    submission_id = serializers.IntegerField()
    started_at = serializers.DateTimeField()

    deployment_id = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()
    questions_snapshot_json = serializers.JSONField()

    exam_id = serializers.IntegerField()
    exam_title = serializers.CharField()
    exam_thumbnail_img_url = serializers.CharField()
    subject_id = serializers.IntegerField()
