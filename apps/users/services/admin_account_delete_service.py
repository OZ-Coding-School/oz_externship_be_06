from apps.users.exceptions import AccountNotFoundError
from apps.users.models import User


def delete_account(account_id: int) -> int:
    try:
        user = User.objects.get(id=account_id)
    except User.DoesNotExist as exc:
        raise AccountNotFoundError from exc

    user.delete()
    return account_id
