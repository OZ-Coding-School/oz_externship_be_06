from apps.users.models import User


class AccountNotFoundError(Exception):
    """회원을 찾을 수 없을 때 발생."""


def delete_account(account_id: int) -> int:
    try:
        user = User.objects.get(id=account_id)
    except User.DoesNotExist as exc:
        raise AccountNotFoundError from exc

    user.delete()
    return account_id
