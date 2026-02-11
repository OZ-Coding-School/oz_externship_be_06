from apps.courses.models import Cohort
from apps.users.exceptions import (
    AlreadyEnrolledError,
    CohortNotFoundError,
    NotUserRoleError,
)
from apps.users.models import StudentEnrollmentRequest, User


def enroll_student(*, user: User, cohort_id: int) -> StudentEnrollmentRequest:
    # 일반 회원 권한 확인
    if user.role != User.Role.USER:
        raise NotUserRoleError("일반 회원만 수강생 등록 신청이 가능합니다.")

    # 기수 존재 확인
    try:
        cohort = Cohort.objects.get(id=cohort_id)
    except Cohort.DoesNotExist as exc:
        raise CohortNotFoundError("존재하지 않는 기수입니다.") from exc

    # 중복 신청 확인
    if StudentEnrollmentRequest.objects.filter(user=user, cohort=cohort).exists():
        raise AlreadyEnrolledError("이미 해당 기수에 등록 신청하였습니다.")

    # 등록 신청 생성
    enrollment_request = StudentEnrollmentRequest.objects.create(
        user=user,
        cohort=cohort,
        status=StudentEnrollmentRequest.Status.PENDING,
    )

    return enrollment_request
