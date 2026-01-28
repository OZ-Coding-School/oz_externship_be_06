from typing import Any

from rest_framework import serializers

from apps.users.models import User
from apps.users.models.enrollment import StudentEnrollmentRequest


class EnrollmentUserSerializer(serializers.Serializer[Any]):
    """등록 요청 유저 정보 시리얼라이저."""

    id = serializers.IntegerField()
    email = serializers.EmailField()
    name = serializers.CharField()
    birthday = serializers.DateField()
    gender = serializers.CharField()


class EnrollmentCohortSerializer(serializers.Serializer[Any]):
    """등록 요청 기수 정보 시리얼라이저."""

    id = serializers.IntegerField()
    number = serializers.IntegerField()


class EnrollmentCourseSerializer(serializers.Serializer[Any]):
    """등록 요청 과정 정보 시리얼라이저."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    tag = serializers.CharField()


class AdminStudentEnrollmentListSerializer(serializers.ModelSerializer[StudentEnrollmentRequest]):
    """어드민 수강생 등록 요청 목록 시리얼라이저."""

    user = serializers.SerializerMethodField()
    cohort = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = StudentEnrollmentRequest
        fields = [
            "id",
            "user",
            "cohort",
            "course",
            "status",
            "created_at",
        ]

    def get_user(self, obj: StudentEnrollmentRequest) -> dict[str, Any]:
        user: User = obj.user
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "birthday": user.birthday,
            "gender": user.gender,
        }

    def get_cohort(self, obj: StudentEnrollmentRequest) -> dict[str, Any]:
        return {
            "id": obj.cohort.id,
            "number": obj.cohort.number,
        }

    def get_course(self, obj: StudentEnrollmentRequest) -> dict[str, Any]:
        return {
            "id": obj.cohort.course.id,
            "name": obj.cohort.course.name,
            "tag": obj.cohort.course.tag,
        }

    def get_status(self, obj: StudentEnrollmentRequest) -> str:
        # 모델은 APPROVED, 명세서는 ACCEPTED
        if obj.status == StudentEnrollmentRequest.Status.APPROVED:
            return "ACCEPTED"
        return obj.status
