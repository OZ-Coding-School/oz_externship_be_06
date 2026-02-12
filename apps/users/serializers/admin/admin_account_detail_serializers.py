from typing import Any

from rest_framework import serializers

from apps.courses.models import Cohort, Course
from apps.users.models import User
from apps.users.services.assigned_courses_service import get_assigned_courses


# 과정 정보 시리얼라이저
class CourseSerializer(serializers.ModelSerializer[Course]):

    class Meta:
        model = Course
        fields = ["id", "name", "tag"]


# 기수정보 시시리엉라이저
class CohortSerializer(serializers.ModelSerializer[Cohort]):

    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Cohort
        fields = ["id", "number", "status", "status_display", "start_date", "end_date"]


# 담당 기수 정보 - 조교 랑 수강생용
class AssignedCohortSerializer(serializers.Serializer[Any]):

    course = CourseSerializer()
    cohort = CohortSerializer()


# 담당 과정 정보 - 러닝코치 운매 전용
class AssignedCourseSerializer(serializers.Serializer[Any]):

    course = CourseSerializer()


# 어드민 회원 상세 조회 응답
class AdminAccountDetailResponseSerializer(serializers.ModelSerializer[User]):

    gender = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
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

    def get_gender(self, obj: User) -> str:
        return obj.gender

    def get_role(self, obj: User) -> str:
        return obj.role

    def get_status(self, obj: User) -> str:
        if not obj.is_active:
            return "DEACTIVATED"
        if hasattr(obj, "withdrawal") and obj.withdrawal is not None:
            return "WITHDREW"
        return "ACTIVATED"

    def get_assigned_courses(self, obj: User) -> list[dict[str, Any]]:
        return get_assigned_courses(obj)
