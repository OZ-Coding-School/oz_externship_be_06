from typing import Any

from rest_framework import serializers

from apps.qna.constants import ANSWER_STATUS_CHOICES, SORT_CHOICES, ErrorMessages


class AdminQuestionListQuerySerializer(serializers.Serializer[Any]):
    """
    어드민 질의응답 목록 조회 쿼리 파라미터 검증 시리얼라이저
    """

    page = serializers.IntegerField(required=False, default=1, min_value=1)
    size = serializers.IntegerField(required=False, default=20, min_value=1)
    search_keyword = serializers.CharField(required=False, allow_blank=True)
    category_id = serializers.IntegerField(required=False)
    answer_status = serializers.ChoiceField(choices=ANSWER_STATUS_CHOICES, required=False)
    sort = serializers.ChoiceField(choices=SORT_CHOICES, required=False, default=SORT_CHOICES[0])

    default_error_message = ErrorMessages.INVALID_ADMIN_QUESTION_LIST
