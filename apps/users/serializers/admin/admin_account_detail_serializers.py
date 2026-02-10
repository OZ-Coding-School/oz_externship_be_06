from typing import Any, Dict, List

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
    """조교(CohortAssistant) 및 수강생(CohortStudent)용: 과정 + 기수 정보"""

    # AttributeError 해결: 중간 모델에서 cohort를 거쳐 course에 접근하도록 source 명시
    course = CourseSerializer(source="cohort.course")
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
        권한에 따른 담당/수강 정보를 반환합니다.
        변수명을 분리하여 mypy [assignment] 에러를 방지합니다.
        """
        # 1. 조교(TA)
        if obj.role == User.Role.TA:
            ta_qs = obj.assisted_cohorts.select_related("cohort__course").all()
            return list(AssignedCohortSerializer(ta_qs, many=True).data)

        # 2. 수강생(STUDENT)
        if obj.role == User.Role.STUDENT:
            student_qs = obj.cohort_students.select_related("cohort__course").all()
            return list(AssignedCohortSerializer(student_qs, many=True).data)

        # 3. 러닝코치(LC)
        if obj.role == User.Role.LC:
            lc_qs = obj.coached_courses.select_related("course").all()
            return list(AssignedCourseSerializer(lc_qs, many=True).data)

        # 4. 운영매니저(OM)
        if obj.role == User.Role.OM:
            om_qs = obj.managed_courses.select_related("course").all()
            return list(AssignedCourseSerializer(om_qs, many=True).data)

        return []
