from django.db import transaction
from django.utils import timezone

from apps.courses.models.cohort_students import CohortStudent
from apps.users.models import User
from apps.users.models.enrollment import StudentEnrollmentRequest


# 수강생 등록 요청을 일괄 승인
def accept_enrollments(enrollment_ids: list[int]) -> int:

    with transaction.atomic():
        enrollments = list(
            StudentEnrollmentRequest.objects.filter(
                id__in=enrollment_ids,
                status=StudentEnrollmentRequest.Status.PENDING,
            ).select_related("user", "cohort")
        )

        if not enrollments:
            return 0

        enrollment_pks = [e.pk for e in enrollments]
        user_ids = [e.user_id for e in enrollments]

        # 등록 요청 일괄 승인
        StudentEnrollmentRequest.objects.filter(pk__in=enrollment_pks).update(
            status=StudentEnrollmentRequest.Status.APPROVED,
            accepted_at=timezone.now(),
        )

        # 유저 role 일괄 변경
        User.objects.filter(id__in=user_ids).update(role=User.Role.STUDENT)

        # CohortStudent 일괄 생성 - 이미 존재하면 무시
        existing_pairs = set(
            CohortStudent.objects.filter(
                user_id__in=user_ids,
            ).values_list("user_id", "cohort_id")
        )
        new_cohort_students = [
            CohortStudent(user=e.user, cohort=e.cohort)
            for e in enrollments
            if (e.user_id, e.cohort_id) not in existing_pairs
        ]
        if new_cohort_students:
            CohortStudent.objects.bulk_create(new_cohort_students)

    return len(enrollments)


# 수강생 등록 요청을 일괄 거절
def reject_enrollments(enrollment_ids: list[int]) -> int:
    with transaction.atomic():
        count = StudentEnrollmentRequest.objects.filter(
            id__in=enrollment_ids,
            status=StudentEnrollmentRequest.Status.PENDING,
        ).update(status=StudentEnrollmentRequest.Status.REJECTED)

    return count
