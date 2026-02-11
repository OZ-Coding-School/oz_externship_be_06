from rest_framework.exceptions import ValidationError
from apps.users.models.withdrawal import Withdrawal
from django.db import transaction
from apps.users.models import User

def withdraw_user(*, user: User, reason: str, reason_detail: str) -> None:
    if not user.is_active:
        raise ValidationError({"error_detail": "이미 탈퇴 신청한 계정입니다."})

    if Withdrawal.objects.filter(user=user).exists():
        raise ValidationError({"error_detail": "이미 탈퇴 신청한 계정입니다."})

    with transaction.atomic():
        Withdrawal.objects.create(
            user=user,
            reason=reason,
            reason_detail=reason_detail,
        )
        user.is_active = False
        user.save(update_fields=["is_active"])