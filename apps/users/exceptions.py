# 회원 관련 예외
class AccountNotFoundError(Exception):
    """회원을 찾을 수 없을 때 발생."""


class AccountUpdateConflictError(Exception):
    """회원 정보 수정 중 충돌 발생 시."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(message)


class StudentNotFoundError(Exception):
    """학생을 찾을 수 없을 때 발생."""


# 휴대폰 인증 관련 예외
class PhoneNumberAlreadyExistsError(Exception):
    """이미 등록된 휴대폰 번호일 때 발생."""


class InvalidPhoneTokenError(Exception):
    """유효하지 않은 휴대폰 인증 토큰일 때 발생."""


# 탈퇴 관련 예외
class WithdrawalNotFoundError(Exception):
    """탈퇴 내역을 찾을 수 없을 때 발생."""


# 수강 등록 관련 예외
class AlreadyEnrolledError(Exception):
    """이미 해당 기수에 등록 신청한 경우."""


class NotUserRoleError(Exception):
    """일반 회원 권한이 아닌 경우."""


class CohortNotFoundError(Exception):
    """기수를 찾을 수 없는 경우."""
