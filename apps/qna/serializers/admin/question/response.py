from typing import Any

from rest_framework import serializers


class AdminQuestionDeleteResponseSerializer(serializers.Serializer[Any]):
    """
    어드민 질의응답 삭제 응답 시리얼라이저
    """

    question_id = serializers.IntegerField()
    deleted_answer_count = serializers.IntegerField()
    deleted_comment_count = serializers.IntegerField()
