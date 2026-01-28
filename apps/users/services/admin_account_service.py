from typing import Any

from django.db import IntegrityError, transaction

from apps.users.models import User


class AccountNotFoundError(Exception):
    """회원을 찾을 수 없을 때 발생."""


class AccountUpdateConflictError(Exception):
    """회원 정보 수정 중 충돌 발생 시."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(message)


# 회원 정보 수정
def update_account(account_id: int, data: dict[str, Any]) -> User:
    try:
        user = User.objects.get(id=account_id)
    except User.DoesNotExist as exc:
        raise AccountNotFoundError from exc

    # 전화번호 중복 체크
    phone_number = data.get("phone_number")
    if phone_number:
        existing = User.objects.filter(phone_number=phone_number).exclude(id=account_id).first()
        if existing:
            raise AccountUpdateConflictError(
                field="phone_number",
                message="휴대폰 번호 중복으로 인하여 요청 처리에 실패하였습니다.",
            )

    # 닉네임 중복 체크
    nickname = data.get("nickname")
    if nickname:
        existing = User.objects.filter(nickname=nickname).exclude(id=account_id).first()
        if existing:
            raise AccountUpdateConflictError(
                field="nickname",
                message="닉네임 중복으로 인하여 요청 처리에 실패하였습니다.",
            )

    try:
        with transaction.atomic():
            for field, value in data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            user.save()
    except IntegrityError as exc:
        raise AccountUpdateConflictError(
            field="unknown",
            message="회원 정보 수정 중 충돌이 발생했습니다.",
        ) from exc

    return user
