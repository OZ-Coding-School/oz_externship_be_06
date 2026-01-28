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
        # prefetch된 cohort_students에서 첫 번째 항목 사용
        cohort_students = getattr(obj, "prefetched_cohort_students", None)
        if cohort_students:
            cs = cohort_students[0] if cohort_students else None
            if cs:
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

        # prefetch가 없는 경우 직접 조회
        cohort_student = obj.cohort_students.select_related("cohort__course").first()
        if cohort_student:
            return {
                "cohort": {
                    "id": cohort_student.cohort.id,
                    "number": cohort_student.cohort.number,
                },
                "course": {
                    "id": cohort_student.cohort.course.id,
                    "name": cohort_student.cohort.course.name,
                    "tag": cohort_student.cohort.course.tag,
                },
            }

        return None
