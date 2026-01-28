from apps.users.models import User


class AccountNotFoundError(Exception):
    """회원을 찾을 수 없을 때 발생."""


# 회원 상세 정보 조회
def get_account_detail(account_id: int) -> User:
    try:
        user = User.objects.get(id=account_id)
    except User.DoesNotExist as exc:
        raise AccountNotFoundError from exc

    return user
