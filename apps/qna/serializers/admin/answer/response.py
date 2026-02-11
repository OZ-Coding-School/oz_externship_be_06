from typing import Any

from rest_framework import serializers


# ==============================================================================
# [DELETE] Admin Answer Delete
# /api/v1/admin/qna/answers/{answer_id}
# ==============================================================================
class AdminAnswerDeleteResponseSerializer(serializers.Serializer[Any]):
    """
    어드민 답변 삭제 응답 시리얼라이저
    """

    answer_id = serializers.IntegerField()
    deleted_comment_count = serializers.IntegerField()
