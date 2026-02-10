from typing import Any, Dict, List, Optional

from rest_framework import serializers

from apps.courses.models import Cohort, Course
from apps.users.models import User


class AdminAccountRoleUpdateSerializer(serializers.Serializer[Any]):
    """
    어드민 유저 권한 변경 요청 시리얼라이저
    """

    role = serializers.ChoiceField(
        choices=User.Role.choices,  # 모델에 정의된 choices를 활용하여 유지보수성 향상
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

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # mypy 에러 방지를 위한 타입 명시 및 추출
        role: Optional[str] = attrs.get("role")
        cohort: Optional[Cohort] = attrs.get("cohort_id")
        courses: Optional[List[Course]] = attrs.get("assigned_courses")

        # 1. 조교(TA) 또는 수강생(STUDENT) 권한 검증
        if role in (User.Role.TA, User.Role.STUDENT):
            if not cohort:
                raise serializers.ValidationError({"cohort_id": f"{role} 권한으로 변경 시 기수 선택은 필수입니다."})

        # 2. 러닝코치(LC) 또는 운영매니저(OM) 권한 검증
        if role in (User.Role.LC, User.Role.OM):
            if not courses:
                raise serializers.ValidationError(
                    {"assigned_courses": f"{role} 권한으로 변경 시 담당 과정 선택은 필수입니다."}
                )

        return attrs
