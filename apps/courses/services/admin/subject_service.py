from typing import Any

from django.db import transaction
from django.db.models import QuerySet

from apps.courses.models import Course, Subject
from apps.courses.utils.constants import ErrorMessages
from apps.exams.models import ExamSubmission


class SubjectNotFoundError(Exception):
    pass


class CourseNotFoundError(Exception):
    pass


class SubjectAlreadyExistsError(Exception):
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

    @staticmethod
    @transaction.atomic
    def create_subject(data: dict[str, Any]) -> Subject:
        course_id = data.pop("course_id")

        # 과정 존재 여부 확인
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise CourseNotFoundError(ErrorMessages.COURSE_NOT_FOUND.value)

        # 동일 과정 내 중복 과목명 체크
        if Subject.objects.filter(course=course, title=data["title"]).exists():
            raise SubjectAlreadyExistsError(ErrorMessages.SUBJECT_ALREADY_EXISTS.value)

        subject = Subject.objects.create(course=course, **data)
        return subject
