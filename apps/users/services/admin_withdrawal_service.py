from django.db import transaction
from django.db.models import Q, QuerySet

from apps.users.exceptions import WithdrawalNotFoundError
from apps.users.models import User, Withdrawal
from apps.users.services.assigned_courses_service import get_assigned_courses

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
        queryset = queryset.filter(Q(user__email__icontains=search) | Q(user__name__icontains=search))

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


# 탈퇴내역 상세 정보 조회
def get_withdrawal_detail(withdrawal_id: int) -> Withdrawal:

    try:
        return (
            Withdrawal.objects.select_related("user")
            .prefetch_related(
                "user__cohort_students__cohort__course",
                "user__assisted_cohorts__cohort__course",
                "user__managed_courses__course",
                "user__coached_courses__course",
            )
            .get(id=withdrawal_id)
        )
    except Withdrawal.DoesNotExist as exc:
        raise WithdrawalNotFoundError from exc


# 탈퇴 취소 (회원 복구)
def cancel_withdrawal(withdrawal_id: int) -> None:
    try:
        withdrawal = Withdrawal.objects.select_related("user").get(id=withdrawal_id)
    except Withdrawal.DoesNotExist as exc:
        raise WithdrawalNotFoundError from exc

    user = withdrawal.user

    with transaction.atomic():
        withdrawal.delete()
        if user:
            user.is_active = True
            user.save(update_fields=["is_active"])
