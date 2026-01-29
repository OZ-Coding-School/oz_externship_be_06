from django.db.models import QuerySet

from apps.courses.models import Cohort


class CohortService:
    @staticmethod
    def get_cohorts_by_course(course_id: int) -> QuerySet[Cohort]:
        return Cohort.objects.filter(course_id=course_id).select_related("course")
