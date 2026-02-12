from typing import Any

from rest_framework import serializers

from apps.users.models import User


# 기수정보 시리얼라이저
class CohortInfoSerializer(serializers.Serializer[Any]):

    id = serializers.IntegerField()
    number = serializers.IntegerField()


# 과정정보
class CourseInfoSerializer(serializers.Serializer[Any]):

    id = serializers.IntegerField()
    name = serializers.CharField()
    tag = serializers.CharField()


# 수강중인 과정정보
class InProgressCourseSerializer(serializers.Serializer[Any]):

    cohort = CohortInfoSerializer()
    course = CourseInfoSerializer()


# 어드민 수강생 목록 조회
class AdminStudentListSerializer(serializers.ModelSerializer[User]):

    status = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    in_progress_course = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nickname",
            "name",
            "phone_number",
            "birthday",
            "status",
            "role",
            "in_progress_course",
            "created_at",
        ]

    def get_status(self, obj: User) -> str:
        if not obj.is_active:
            return "DEACTIVATED"
        if hasattr(obj, "withdrawal") and obj.withdrawal is not None:
            return "WITHDREW"
        return "ACTIVATED"

    def get_role(self, obj: User) -> str:
        return obj.role

    def get_in_progress_course(self, obj: User) -> dict[str, Any] | None:
        cohort_students = obj.cohort_students.all()
        if not cohort_students:
            return None

        cs = cohort_students[0]
        return {
            "cohort": {
                "id": cs.cohort.id,
                "number": cs.cohort.number,
            },
            "course": {
                "id": cs.cohort.course.id,
                "name": cs.cohort.course.name,
                "tag": cs.cohort.course.tag,
            },
        }
