from typing import Any

from django.db.models import Avg, OuterRef, Subquery

from apps.courses.models import Cohort, Course
from apps.courses.services.course_service import CourseNotFoundError
from apps.courses.utils.constants import ErrorMessages
from apps.exams.models import ExamSubmission

__all__ = ["AdminCohortService", "CohortNotFoundError", "CourseNotFoundError"]


class CohortNotFoundError(Exception):
    pass


class AdminCohortService:
    @staticmethod
    def create_cohort(validated_data: dict[str, Any]) -> Cohort:
        course_id: int = validated_data["course_id"]
        if not Course.objects.filter(id=course_id).exists():
            raise CourseNotFoundError(ErrorMessages.COURSE_NOT_FOUND.value)
        return Cohort.objects.create(**validated_data)

    @staticmethod
    def get_cohort(cohort_id: int) -> Cohort:
        try:
            return Cohort.objects.select_related("course").get(id=cohort_id)
        except Cohort.DoesNotExist:
            raise CohortNotFoundError(ErrorMessages.COHORT_NOT_FOUND.value)

    @staticmethod
    def update_cohort(cohort: Cohort, validated_data: dict[str, Any]) -> Cohort:
        for field, value in validated_data.items():
            setattr(cohort, field, value)
        cohort.save()
        return cohort

    @staticmethod
    def validate_course_exists(course_id: int) -> None:
        if not Course.objects.filter(id=course_id).exists():
            raise CourseNotFoundError(ErrorMessages.COURSE_NOT_FOUND.value)

    @staticmethod
    def get_cohort_avg_scores(course_id: int) -> list[dict[str, Any]]:
        avg_subquery = (
            ExamSubmission.objects.filter(submitter__cohort_students__cohort=OuterRef("pk"))
            .values("submitter__cohort_students__cohort")
            .annotate(avg=Avg("score"))
            .values("avg")
        )

        cohorts = (
            Cohort.objects.filter(course_id=course_id).annotate(avg_score=Subquery(avg_subquery)).order_by("number")
        )

        return [
            {"name": f"{cohort.number}기", "score": int(cohort.avg_score) if cohort.avg_score else 0}
            for cohort in cohorts
        ]

    @staticmethod
    def get_students(cohort: Cohort) -> list[dict[str, Any]]:
        students = cohort.cohort_students.select_related("user").all()

        return [{"value": cs.user.nickname, "label": cs.user.name} for cs in students]
