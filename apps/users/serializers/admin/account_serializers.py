from typing import Any
from django.apps import apps
from rest_framework import serializers
from apps.users.models import User

class AdminCourseDetailSerializer(serializers.ModelSerializer[Any]):
    """수강 중인 코스 및 기수의 상세 정보 시리얼라이저"""
    course = serializers.SerializerMethodField()
    cohort = serializers.SerializerMethodField()

    class Meta:
        # Enrollment 모델을 직접 임포트하지 않고 문자열로 참조하여 ImportError 방지
        model = apps.get_model('courses', 'Enrollment')
        fields = ["course", "cohort"]

    def get_course(self, obj: Any) -> dict[str, Any]:
        return {
            "id": obj.course.id,
            "name": obj.course.name,
            "tag": obj.course.tag
        }

    def get_cohort(self, obj: Any) -> dict[str, Any]:
        return {
            "id": obj.cohort.id,
            "number": obj.cohort.number,
            "status": obj.cohort.status,
            "start_date": obj.cohort.start_date.isoformat() if obj.cohort.start_date else None,
            "end_date": obj.cohort.end_date.isoformat() if obj.cohort.end_date else None,
        }

class AdminAccountBaseSerializer(serializers.ModelSerializer[Any]):
    """공통 필드 로직을 처리하는 베이스 시리얼라이저"""
    status = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    birthday = serializers.DateField(format="%Y-%m-%d")
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f%z")

    def get_status(self, obj: User) -> str:
        if hasattr(obj, "withdrawal") and obj.withdrawal is not None:
            return "withdrew"
        return "active" if obj.is_active else "inactive"

    def get_role(self, obj: User) -> str:
        return obj.role.lower()

class AdminAccountListSerializer(AdminAccountBaseSerializer):
    """어드민 페이지 회원 목록 조회를 위한 시리얼라이저"""
    class Meta:
        model = User
        fields = ["id", "email", "nickname", "name", "birthday", "status", "role", "created_at"]

class AdminAccountDetailSerializer(AdminAccountBaseSerializer):
    """어드민 페이지 회원 정보 상세 조회를 위한 시리얼라이저"""
    # related_name이 없으므로 Django 기본 역참조 명칭인 enrollment_set 사용
    assigned_courses = AdminCourseDetailSerializer(many=True, source="enrollment_set")
    gender = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "nickname", "name", "phone_number",
            "birthday", "gender", "status", "role",
            "profile_img_url", "assigned_courses", "created_at"
        ]

    def get_gender(self, obj: User) -> str:
        gender_map = {"MALE": "M", "FEMALE": "F"}
        return gender_map.get(obj.gender, obj.gender)