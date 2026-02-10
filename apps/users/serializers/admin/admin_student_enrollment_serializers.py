from typing import Any, Dict

from rest_framework import serializers

from apps.users.models import User
from apps.users.models.enrollment import StudentEnrollmentRequest

# --- 중첩 데이터용 시리얼라이저 ---


class EnrollmentUserSerializer(serializers.ModelSerializer[User]):
    """등록 요청 유저 정보"""

    class Meta:
        model = User
        fields = ["id", "email", "name", "birthday", "gender"]


class EnrollmentCohortSerializer(serializers.Serializer[Any]):
    """등록 요청 기수 정보"""

    id = serializers.IntegerField()
    number = serializers.IntegerField()


class EnrollmentCourseSerializer(serializers.Serializer[Any]):
    """등록 요청 과정 정보"""

    id = serializers.IntegerField()
    name = serializers.CharField()
    tag = serializers.CharField()


# --- 메인 시리얼라이저 ---


class AdminStudentEnrollmentListSerializer(serializers.ModelSerializer[StudentEnrollmentRequest]):
    """어드민 수강생 등록 요청 목록 조회"""

    user = EnrollmentUserSerializer(read_only=True)
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

    def get_cohort(self, obj: StudentEnrollmentRequest) -> Dict[str, Any]:
        # 인스턴스를 넘기기 위해 시리얼라이저 제네릭을 Any로 수정하여 에러 해결
        return dict(EnrollmentCohortSerializer(obj.cohort).data)

    def get_course(self, obj: StudentEnrollmentRequest) -> Dict[str, Any]:
        # 인스턴스를 넘기기 위해 시리얼라이저 제네릭을 Any로 수정하여 에러 해결
        return dict(EnrollmentCourseSerializer(obj.cohort.course).data)

    def get_status(self, obj: StudentEnrollmentRequest) -> str:
        if obj.status == StudentEnrollmentRequest.Status.APPROVED:
            return "ACCEPTED"
        return str(obj.status)


class AdminStudentEnrollmentAcceptSerializer(serializers.Serializer[Dict[str, Any]]):
    """어드민 수강생 등록 요청 승인 (Bulk)"""

    enrollments = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False,
    )


class AdminStudentEnrollmentRejectSerializer(serializers.Serializer[Dict[str, Any]]):
    """어드민 수강생 등록 요청 거절 (Bulk)"""

    enrollments = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False,
    )


class AdminStudentEnrollmentResponseSerializer(serializers.Serializer[Dict[str, Any]]):
    """처리 결과 메시지 응답"""

    detail = serializers.CharField(help_text="처리 결과 메시지")
