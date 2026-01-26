from typing import Any

from apps.courses.models import Cohort
from apps.courses.models.cohort_students import CohortStudent
from apps.users.models import User


# 수강신청 가능한 기수 목록 조회
def get_available_courses() -> list[dict[str, Any]]:
    cohorts = Cohort.objects.filter(status=Cohort.StatusChoices.PREPARING).select_related("course")

    return [
        {
            "cohort": {
                "id": cohort.id,
                "number": cohort.number,
                "start_date": cohort.start_date,
                "end_date": cohort.end_date,
                "status": cohort.status,
            },
            "course": {
                "id": cohort.course.id,
                "name": cohort.course.name,
            },
        }
        for cohort in cohorts
    ]


# 내 수강목록 조회
def get_enrolled_courses(*, user: User) -> list[dict[str, Any]]:
    cohort_students = CohortStudent.objects.filter(user=user).select_related(  # type: ignore[attr-defined]
        "cohort__course"
    )

    return [
        {
            "cohort": {
                "id": cs.cohort.id,
                "number": cs.cohort.number,
                "start_date": cs.cohort.start_date,
                "end_date": cs.cohort.end_date,
                "status": cs.cohort.status,
            },
            "course": {
                "id": cs.cohort.course.id,
                "name": cs.cohort.course.name,
                "tag": cs.cohort.course.tag,
                "thumbnail_img_url": cs.cohort.course.thumbnail_img_url,
            },
        }
        for cs in cohort_students
    ]
