from apps.courses.models import Cohort, CohortStudent, Course
from apps.courses.models.learning_coachs import LearningCoach
from apps.courses.models.operation_managers import OperationManager
from apps.courses.models.training_assistants import TrainingAssistant
from apps.users.models import User


class AccountNotFoundError(Exception):
    """회원을 찾을 수 없을 때"""


def update_account_role(
    account_id: int,
    role: str,
    cohort: Cohort | None = None,
    assigned_courses: list[Course] | None = None,
) -> User:
    try:
        user = User.objects.get(id=account_id)
    except User.DoesNotExist as exc:
        raise AccountNotFoundError from exc

    old_role = user.role

    # 기존 역할 관련 데이터 삭제
    _clear_role_relations(user, old_role)

    # 새 역할 설정
    user.role = role
    user.save()

    # 새 역할 관련 데이터 생성
    _create_role_relations(user, role, cohort, assigned_courses)

    return user


# 기존 역할 관련 데이터 삭제
def _clear_role_relations(user: User, role: str) -> None:
    if role == User.Role.TA:
        TrainingAssistant.objects.filter(user=user).delete()
    elif role == User.Role.LC:
        LearningCoach.objects.filter(user=user).delete()
    elif role == User.Role.OM:
        OperationManager.objects.filter(user=user).delete()
    elif role == User.Role.STUDENT:
        CohortStudent.objects.filter(user=user).delete()


def _create_role_relations(
    user: User,
    role: str,
    cohort: Cohort | None,
    assigned_courses: list[Course] | None,
) -> None:
    if role == User.Role.TA and cohort:  # 새 역할 데이터 생성
        TrainingAssistant.objects.create(user=user, cohort=cohort)
    elif role == User.Role.STUDENT and cohort:
        CohortStudent.objects.create(user=user, cohort=cohort)
    elif role == User.Role.LC and assigned_courses:
        for course in assigned_courses:
            LearningCoach.objects.create(user=user, course=course)
    elif role == User.Role.OM and assigned_courses:
        for course in assigned_courses:
            OperationManager.objects.create(user=user, course=course)
