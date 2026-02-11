from typing import Any

from apps.courses.models import CohortStudent
from apps.courses.models.learning_coachs import LearningCoach
from apps.courses.models.operation_managers import OperationManager
from apps.courses.models.training_assistants import TrainingAssistant
from apps.users.models import User


# 과정 정보 딕셔러니 생성
def _build_course_dict(course: Any) -> dict[str, Any]:
    return {
        "id": course.id,
        "name": course.name,
        "tag": course.tag,
    }


# 기수 정보 딕셔너리 생성
def _build_cohort_dict(cohort: Any) -> dict[str, Any]:
    return {
        "id": cohort.id,
        "number": cohort.number,
        "status": cohort.status,
        "status_display": cohort.get_status_display(),
        "start_date": cohort.start_date,
        "end_date": cohort.end_date,
    }


# 수강생의 수강 과정 기수 목록을 반환
def get_assigned_courses_for_student(user: User) -> list[dict[str, Any]]:
    cohort_students = CohortStudent.objects.filter(user=user).select_related("cohort__course")
    return [
        {
            "course": _build_course_dict(cs.cohort.course),
            "cohort": _build_cohort_dict(cs.cohort),
        }
        for cs in cohort_students
    ]


# 조교의 담당 과정-기수 목록을 반환
def get_assigned_courses_for_ta(user: User) -> list[dict[str, Any]]:
    training_assistants = TrainingAssistant.objects.filter(user=user).select_related("cohort__course")
    return [
        {
            "course": _build_course_dict(ta.cohort.course),
            "cohort": _build_cohort_dict(ta.cohort),
        }
        for ta in training_assistants
    ]


# 운영매니저의 담당 과정 목록을 반환
def get_assigned_courses_for_om(user: User) -> list[dict[str, Any]]:
    operation_managers = OperationManager.objects.filter(user=user).select_related("course")
    return [{"course": _build_course_dict(om.course)} for om in operation_managers]


# 러닝코치의 담당 과정 목록을 반환
def get_assigned_courses_for_lc(user: User) -> list[dict[str, Any]]:
    learning_coachs = LearningCoach.objects.filter(user=user).select_related("course")
    return [{"course": _build_course_dict(lc.course)} for lc in learning_coachs]


# 유저 권한에 따라 담당/수강 과정 목록을 반환
def get_assigned_courses(user: User) -> list[dict[str, Any]]:
    if user.role == User.Role.STUDENT:
        return get_assigned_courses_for_student(user)
    elif user.role == User.Role.TA:
        return get_assigned_courses_for_ta(user)
    elif user.role == User.Role.OM:
        return get_assigned_courses_for_om(user)
    elif user.role == User.Role.LC:
        return get_assigned_courses_for_lc(user)
    return []
