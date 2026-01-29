from typing import Any

from django.db.models import QuerySet

from apps.courses.models import Subject
from apps.courses.utils.constants import ErrorMessages
from apps.exams.models import ExamSubmission


class SubjectNotFoundError(Exception):
    pass


class SubjectListService:
    @staticmethod
    def get_subjects_by_course(course_id: int) -> QuerySet[Subject]:
        return Subject.objects.filter(course_id=course_id).select_related("course")


class AdminSubjectService:
    @staticmethod
    def validate_subject_exists(subject_id: int) -> Subject:
        try:
            return Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            raise SubjectNotFoundError(ErrorMessages.SUBJECT_NOT_FOUND.value)

    @staticmethod
    def get_scatter_data(subject: Subject) -> list[dict[str, Any]]:
        submissions = ExamSubmission.objects.filter(deployment__exam__subject=subject).select_related("deployment")

        result = []
        for submission in submissions:
            if submission.started_at is None:
                continue
            elapsed_seconds = (submission.created_at - submission.started_at).total_seconds()
            elapsed_hours = round(elapsed_seconds / 3600, 1)

            result.append({"time": elapsed_hours, "score": submission.score})

        return result
