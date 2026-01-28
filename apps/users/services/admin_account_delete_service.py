from apps.users.models import User


class AccountNotFoundError(Exception):
    """회원을 찾을 수 없을 때 발생."""


def delete_account(account_id: int) -> int:
    """회원 정보를 삭제합니다.

    Args:
        account_id: 삭제할 회원 ID

    Returns:
        삭제된 회원 ID

    Raises:
        AccountNotFoundError: 회원을 찾을 수 없을 때
    """
    try:
        user = User.objects.get(id=account_id)
    except User.DoesNotExist as exc:
        raise AccountNotFoundError from exc

    user.delete()
    return account_id
