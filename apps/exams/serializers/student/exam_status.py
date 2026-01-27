from __future__ import annotations

from typing import Any

from rest_framework import serializers


class ExamStatusResponseSerializer(serializers.Serializer[Any]):
    exam_status = serializers.CharField(help_text="시험 상태 (in_progress, closed)")
    force_submit = serializers.BooleanField(help_text="강제 제출 여부")
