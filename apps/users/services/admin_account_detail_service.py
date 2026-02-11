from apps.users.exceptions import AccountNotFoundError
from apps.users.models import User


# 회원 상세 정보 조회
def get_account_detail(account_id: int) -> User:
    try:
        user = User.objects.get(id=account_id)
    except User.DoesNotExist as exc:
        raise AccountNotFoundError from exc

    return user
