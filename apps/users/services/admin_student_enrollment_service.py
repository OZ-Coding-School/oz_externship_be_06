from django.db import transaction
from django.utils import timezone

from apps.courses.models.cohort_students import CohortStudent
from apps.users.models import User
from apps.users.models.enrollment import StudentEnrollmentRequest


# 수강생 등록 요청을 일괄 승인
def accept_enrollments(enrollment_ids: list[int]) -> int:

    with transaction.atomic():
        enrollments = StudentEnrollmentRequest.objects.filter(
            id__in=enrollment_ids,
            status=StudentEnrollmentRequest.Status.PENDING,
        ).select_related("user", "cohort")

        count = 0
        for enrollment in enrollments:
            # 등록 요청 승인 처리
            enrollment.status = StudentEnrollmentRequest.Status.APPROVED
            enrollment.accepted_at = timezone.now()
            enrollment.save()

            # 유저 role 변경
            user = enrollment.user
            user.role = User.Role.STUDENT
            user.save(update_fields=["role"])

            # CohortStudent 생성 (이미 존재하지 않는 경우)
            CohortStudent.objects.get_or_create(
                user=user,
                cohort=enrollment.cohort,
            )
            count += 1

    return count


# 수강생 등록 요청을 일괄 거절
def reject_enrollments(enrollment_ids: list[int]) -> int:
    with transaction.atomic():
        count = StudentEnrollmentRequest.objects.filter(
            id__in=enrollment_ids,
            status=StudentEnrollmentRequest.Status.PENDING,
        ).update(status=StudentEnrollmentRequest.Status.REJECTED)

    return count
