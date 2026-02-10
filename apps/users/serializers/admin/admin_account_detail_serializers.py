from typing import Any, Dict, List, Union

from django.db.models import QuerySet
from rest_framework import serializers

from apps.courses.models import Cohort, Course
from apps.users.models import User


class CourseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ["id", "name", "tag"]


class CohortSerializer(serializers.ModelSerializer[Cohort]):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Cohort
        fields = ["id", "number", "status", "status_display", "start_date", "end_date"]


class AssignedCohortSerializer(serializers.Serializer[Any]):
    """조교 및 수강생용: 과정 + 기수 정보"""

    course = CourseSerializer()
    cohort = CohortSerializer()


class AssignedCourseSerializer(serializers.Serializer[Any]):
    """러닝코치 및 운영매니저용: 과정 정보 전용"""

    course = CourseSerializer()


class AdminAccountDetailResponseSerializer(serializers.ModelSerializer[User]):
    gender = serializers.CharField()
    role = serializers.CharField()
    status = serializers.SerializerMethodField()
    assigned_courses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nickname",
            "name",
            "phone_number",
            "birthday",
            "gender",
            "role",
            "status",
            "profile_img_url",
            "created_at",
            "assigned_courses",
        ]

    def get_status(self, obj: User) -> str:
        if not obj.is_active:
            return "DEACTIVATED"
        if hasattr(obj, "withdrawals") and obj.withdrawals.exists():
            return "WITHDREW"
        return "ACTIVATED"

    def get_assigned_courses(self, obj: User) -> List[Dict[str, Any]]:
        """
        권한에 따른 담당/수강 정보 반환
        """
        # 에러 해결: 서로 다른 모델의 QuerySet을 하나의 변수에 담을 때 발생하는 [assignment] 에러 해결을 위해
        # Union 타입을 사용하거나, 각 분기에서 즉시 처리합니다.

        if obj.role == User.Role.TA:
            queryset = obj.assisted_cohorts.select_related("cohort__course").all()
            return list(AssignedCohortSerializer(queryset, many=True).data)

        if obj.role == User.Role.STUDENT:
            # 변수명을 분리하거나 타입을 명시적으로 지정하여 assignment 에러 방지
            student_queryset = obj.cohort_students.select_related("cohort__course").all()
            return list(AssignedCohortSerializer(student_queryset, many=True).data)

        if obj.role == User.Role.LC:
            lc_queryset = obj.coached_courses.select_related("course").all()
            return list(AssignedCourseSerializer(lc_queryset, many=True).data)

        if obj.role == User.Role.OM:
            om_queryset = obj.managed_courses.select_related("course").all()
            return list(AssignedCourseSerializer(om_queryset, many=True).data)

        return []
