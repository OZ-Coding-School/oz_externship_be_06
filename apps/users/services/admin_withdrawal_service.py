from typing import Any

from django.db.models import Q, QuerySet

from apps.courses.models import CohortStudent
from apps.courses.models.learning_coachs import LearningCoach
from apps.courses.models.operation_managers import OperationManager
from apps.courses.models.training_assistants import TrainingAssistant
from apps.users.models import User, Withdrawal


class WithdrawalNotFoundError(Exception):
    """탈퇴 내역을 찾을 수 없을 때 발생."""


# role 파라미터 매핑
ROLE_MAP = {
    "user": User.Role.USER,
    "training_assistant": User.Role.TA,
    "operation_manager": User.Role.OM,
    "learning_coach": User.Role.LC,
    "admin": User.Role.ADMIN,
    "student": User.Role.STUDENT,
}


def get_withdrawal_list(
    search: str | None = None,
    role: str | None = None,
    sort: str | None = None,
) -> QuerySet[Withdrawal]:
    queryset = Withdrawal.objects.select_related("user")

    # 검색 필터 (이메일, 이름)
    if search:
        queryset = queryset.filter(
            Q(user__email__icontains=search) | Q(user__name__icontains=search)
        )

    # 권한 필터
    if role and role.lower() in ROLE_MAP:
        queryset = queryset.filter(user__role=ROLE_MAP[role.lower()])

    # 정렬
    if sort == "latest":
        queryset = queryset.order_by("-created_at")
    elif sort == "oldest":
        queryset = queryset.order_by("created_at")
    else:
        queryset = queryset.order_by("id")

    return queryset

#수강생의 수강 과정-기수 목록을 반환
def _get_assigned_courses_for_student(user: User) -> list[dict[str, Any]]:
    cohort_students = CohortStudent.objects.filter(user=user).select_related(
        "cohort__course"
    )
    return [
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
                "start_date": cs.cohort.start_date,
                "end_date": cs.cohort.end_date,
            },
        }
        for cs in cohort_students
    ]

#조교의 담당 과정-기수 목록을 반환
def _get_assigned_courses_for_ta(user: User) -> list[dict[str, Any]]:
    training_assistants = TrainingAssistant.objects.filter(user=user).select_related(
        "cohort__course"
    )
    return [
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
                "start_date": ta.cohort.start_date,
                "end_date": ta.cohort.end_date,
            },
        }
        for ta in training_assistants
    ]

#운영매니저의 담당 과정 목록을 반환
def _get_assigned_courses_for_om(user: User) -> list[dict[str, Any]]:
    operation_managers = OperationManager.objects.filter(user=user).select_related(
        "course"
    )
    return [
        {
            "course": {
                "id": om.course.id,
                "name": om.course.name,
                "tag": om.course.tag,
            },
            "cohort": None,
        }
        for om in operation_managers
    ]

#러닝코치의 담당 과정 목록을 반환
def _get_assigned_courses_for_lc(user: User) -> list[dict[str, Any]]:
    learning_coachs = LearningCoach.objects.filter(user=user).select_related("course")
    return [
        {
            "course": {
                "id": lc.course.id,
                "name": lc.course.name,
                "tag": lc.course.tag,
            },
            "cohort": None,
        }
        for lc in learning_coachs
    ]


def get_assigned_courses(user: User) -> list[dict[str, Any]]:
    """유저의 권한에 따라 담당/수강 과정 목록을 반환합니다."""
    if user.role == User.Role.STUDENT:
        return _get_assigned_courses_for_student(user)
    elif user.role == User.Role.TA:
        return _get_assigned_courses_for_ta(user)
    elif user.role == User.Role.OM:
        return _get_assigned_courses_for_om(user)
    elif user.role == User.Role.LC:
        return _get_assigned_courses_for_lc(user)
    return []


def get_withdrawal_detail(withdrawal_id: int) -> Withdrawal:
    """
    회원 탈퇴 내역 상세 정보를 조회합니다.

    Args:
        withdrawal_id: 탈퇴 내역 ID

    Returns:
        Withdrawal 객체

    Raises:
        WithdrawalNotFoundError: 탈퇴 내역을 찾을 수 없는 경우
    """
    try:
        return Withdrawal.objects.select_related("user").get(id=withdrawal_id)
    except Withdrawal.DoesNotExist as exc:
        raise WithdrawalNotFoundError from exc
