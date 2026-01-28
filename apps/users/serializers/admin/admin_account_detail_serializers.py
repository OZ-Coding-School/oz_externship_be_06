from typing import Any

from rest_framework import serializers

from apps.courses.models import Cohort, Course
from apps.users.models import User


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
        if hasattr(obj, "withdrawals") and obj.withdrawals.exists():
            return "WITHDREW"
        return "ACTIVATED"

    def get_assigned_courses(self, obj: User) -> list[dict[str, Any]]:
        # 권한에 따른 기수 정보 반환
        result: list[dict[str, Any]] = []

        if obj.role == User.Role.TA:
            # 조교: 담당 기수 목록
            for ta in obj.assisted_cohorts.select_related("cohort__course").all():
                result.append(
                    {
                        "course": {
                            "id": ta.cohort.course.id,
                            "name": ta.cohort.course.name,
                            "tag": ta.cohort.course.tag,
                        },
                        "cohort": {
                            "id": ta.cohort.id,
                            "number": ta.cohort.number,
                            "status": ta.cohort.status,
                            "status_display": ta.cohort.get_status_display(),
                            "start_date": ta.cohort.start_date,
                            "end_date": ta.cohort.end_date,
                        },
                    }
                )

        elif obj.role == User.Role.LC:
            # 러닝코치: 담당 과정 목록
            for lc in obj.coached_courses.select_related("course").all():
                result.append(
                    {
                        "course": {
                            "id": lc.course.id,
                            "name": lc.course.name,
                            "tag": lc.course.tag,
                        },
                    }
                )

        elif obj.role == User.Role.OM:
            # 운영매니저: 담당 과정 목록
            for om in obj.managed_courses.select_related("course").all():
                result.append(
                    {
                        "course": {
                            "id": om.course.id,
                            "name": om.course.name,
                            "tag": om.course.tag,
                        },
                    }
                )

        elif obj.role == User.Role.STUDENT:
            # 수강생: 수강 기수 목록
            for cs in obj.cohort_students.select_related("cohort__course").all():
                result.append(
                    {
                        "course": {
                            "id": cs.cohort.course.id,
                            "name": cs.cohort.course.name,
                            "tag": cs.cohort.course.tag,
                        },
                        "cohort": {
                            "id": cs.cohort.id,
                            "number": cs.cohort.number,
                            "status": cs.cohort.status,
                            "status_display": cs.cohort.get_status_display(),
                            "start_date": cs.cohort.start_date,
                            "end_date": cs.cohort.end_date,
                        },
                    }
                )

        return result
