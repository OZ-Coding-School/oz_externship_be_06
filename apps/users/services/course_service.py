from typing import Any

from django.db.models import Prefetch

from apps.courses.models import Cohort, Course
from apps.courses.models.cohort_students import CohortStudent
from apps.users.models import User


# 수강신청 가능한 과정 및 기수 목록 조회
def get_available_courses() -> list[dict[str, Any]]:
    preparing_cohorts = Cohort.objects.filter(status=Cohort.StatusChoices.PREPARING)

    courses = (
        Course.objects.filter(cohorts__status=Cohort.StatusChoices.PREPARING)
        .prefetch_related(Prefetch("cohorts", queryset=preparing_cohorts, to_attr="preparing_cohorts"))
        .distinct()
    )

    return [
        {
            "course": {
                "id": course.id,
                "name": course.name,
            },
            "cohorts": [
                {
                    "id": cohort.id,
                    "number": cohort.number,
                    "start_date": cohort.start_date,
                    "end_date": cohort.end_date,
                }
                for cohort in course.preparing_cohorts  # type: ignore[attr-defined]
            ],
        }
        for course in courses
    ]


# 내 수강목록 조회
def get_enrolled_courses(*, user: User) -> list[dict[str, Any]]:
    cohort_students = CohortStudent.objects.filter(user=user).select_related("cohort__course")

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
