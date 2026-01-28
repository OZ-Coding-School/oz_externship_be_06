from typing import Any

from rest_framework import serializers

from apps.courses.models import Cohort, Course
from apps.users.models import User

#어드민 권한 변경 요철
class AdminAccountRoleUpdateSerializer(serializers.Serializer[Any]):

    role = serializers.ChoiceField(
        choices=[
            ("USER", "일반회원"),
            ("ADMIN", "관리자"),
            ("TA", "조교"),
            ("OM", "운영매니저"),
            ("LC", "러닝코치"),
            ("STUDENT", "수강생"),
        ],
        required=True,
    )
    cohort_id = serializers.PrimaryKeyRelatedField(
        queryset=Cohort.objects.all(),
        required=False,
        allow_null=True,
    )
    assigned_courses = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        many=True,
        required=False,
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        role = attrs.get("role")
        cohort_id = attrs.get("cohort_id")
        assigned_courses = attrs.get("assigned_courses")

        if role in ("TA", "STUDENT") and not cohort_id:
            raise serializers.ValidationError(
                {"cohort_id": [f"{role} 권한으로 변경 시 기수 선택은 필수입니다."]}
            )

        if role in ("LC", "OM") and not assigned_courses:
            raise serializers.ValidationError(
                {"assigned_courses": [f"{role} 권한으로 변경 시 담당 과정 선택은 필수입니다."]}
            )

        return attrs
