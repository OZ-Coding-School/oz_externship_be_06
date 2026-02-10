from typing import Any, Dict, Optional

from rest_framework import serializers

from apps.users.models import User


class CohortInfoSerializer(serializers.Serializer[Any]):
    """기수 정보 시리얼라이저"""

    id = serializers.IntegerField()
    number = serializers.IntegerField()


class CourseInfoSerializer(serializers.Serializer[Any]):
    """과정 정보 시리얼라이저"""

    id = serializers.IntegerField()
    name = serializers.CharField()
    tag = serializers.CharField()


class InProgressCourseSerializer(serializers.Serializer[Any]):
    """수강 중인 과정 상세 정보 (기수 + 과정)"""

    cohort = CohortInfoSerializer()
    course = CourseInfoSerializer()


class AdminStudentListSerializer(serializers.ModelSerializer[User]):
    """어드민 수강생 목록 조회 시리얼라이저"""

    status = serializers.SerializerMethodField()
    role = serializers.CharField()  # 단순 문자열이므로 SerializerMethodField 제거
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
        # 역참조 필드 존재 여부를 더 안전하게 체크
        if hasattr(obj, "withdrawals") and obj.withdrawals.exists():
            return "WITHDREW"
        return "ACTIVATED"

    def get_in_progress_course(self, obj: User) -> Optional[Dict[str, Any]]:
        """
        수강 중인 과정 정보를 반환합니다.
        prefetch_related("cohort_students") 데이터를 우선적으로 사용합니다.
        """
        # 1. prefetch 데이터 확인 (View에서 prefetched_cohort_students로 넘겨준다고 가정)
        cohort_students = getattr(obj, "prefetched_cohort_students", None)

        target_student = None
        if cohort_students:
            target_student = cohort_students[0]
        else:
            # 2. prefetch가 없는 경우 DB 직접 조회
            target_student = obj.cohort_students.select_related("cohort__course").first()

        if not target_student:
            return None

        # 데이터 매핑 (내부 시리얼라이저 재사용)
        data = {
            "cohort": {
                "id": target_student.cohort.id,
                "number": target_student.cohort.number,
            },
            "course": {
                "id": target_student.cohort.course.id,
                "name": target_student.cohort.course.name,
                "tag": target_student.cohort.course.tag,
            },
        }

        # mypy의 ReturnDict 타입 불일치 방지를 위한 dict() 캐스팅
        return dict(InProgressCourseSerializer(data).data)
