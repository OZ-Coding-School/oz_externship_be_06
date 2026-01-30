from typing import Any

from django.apps import apps
from rest_framework import serializers

from apps.users.models import User


class AdminCourseDetailSerializer(serializers.ModelSerializer[Any]):
    """
    상세 정보 내 assigned_courses 항목을 위한 시리얼라이저

    - 기존(users.Enrollment) 참조를 courses.CohortStudent로 변경
    - course 정보는 cohort.course로 접근
    """

    id = serializers.IntegerField(source="cohort.course.id")
    name = serializers.CharField(source="cohort.course.name")
    tag = serializers.CharField(source="cohort.course.tag", default="BE")
    cohort = serializers.SerializerMethodField()

    class Meta:
        model = apps.get_model("courses", "CohortStudent")
        fields = ["id", "name", "tag", "cohort"]

    def get_cohort(self, obj: Any) -> dict[str, Any]:
        return {
            "id": obj.cohort.id,
            "number": obj.cohort.number,
            "status": getattr(obj.cohort, "status", "PREPARING"),
            "start_date": obj.cohort.start_date.strftime("%Y-%m-%d") if obj.cohort.start_date else None,
            "end_date": obj.cohort.end_date.strftime("%Y-%m-%d") if obj.cohort.end_date else None,
        }


class AdminAccountListSerializer(serializers.ModelSerializer[Any]):
    """
    어드민 페이지 회원 목록 조회를 위한 시리얼라이저
    """

    status = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f%z")

    class Meta:
        model = User
        fields = ["id", "email", "nickname", "name", "status", "role", "created_at"]

    def get_status(self, obj: User) -> str:
        if hasattr(obj, "withdrawal") and obj.withdrawal is not None:
            return "withdrew"
        return "active" if obj.is_active else "inactive"

    def get_role(self, obj: User) -> str:
        return obj.role.lower()


class AdminAccountDetailSerializer(serializers.ModelSerializer[Any]):
    """
    어드민 페이지 회원 정보 상세 조회를 위한 시리얼라이저
    """

    status = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    birthday = serializers.DateField(format="%Y-%m-%d")
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f%z")
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
            "status",
            "role",
            "profile_img_url",
            "assigned_courses",
            "created_at",
        ]

    def get_status(self, obj: User) -> str:
        if hasattr(obj, "withdrawal") and obj.withdrawal is not None:
            return "withdrew"
        return "active" if obj.is_active else "inactive"

    def get_role(self, obj: User) -> str:
        return obj.role.lower()

    def get_gender(self, obj: User) -> str:
        return "M" if obj.gender == "MALE" else "F"

    def get_assigned_courses(self, obj: User) -> list[dict[str, Any]]:
        # Mypy 에러("User has no attribute cohort_students" 등)를 피하기 위해
        # get_model로 가져온 모델에서 직접 필터링합니다.
        cohort_student_model = apps.get_model("courses", "CohortStudent")
        cohort_students = cohort_student_model.objects.filter(user=obj).select_related("cohort__course")

        return [
            {
                "course": {
                    "id": cs.cohort.course.id,
                    "name": cs.cohort.course.name,
                    "tag": getattr(cs.cohort.course, "tag", "BE"),
                },
                "cohort": {
                    "id": cs.cohort.id,
                    "number": cs.cohort.number,
                    "status": getattr(cs.cohort, "status", "PREPARING"),
                    "start_date": cs.cohort.start_date.strftime("%Y-%m-%d") if cs.cohort.start_date else None,
                    "end_date": cs.cohort.end_date.strftime("%Y-%m-%d") if cs.cohort.end_date else None,
                },
            }
            for cs in cohort_students
        ]
