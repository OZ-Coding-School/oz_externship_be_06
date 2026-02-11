from __future__ import annotations

from django.db import transaction

from apps.courses.models.subjects import Subject
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models.exams import Exam


def create_exam(title: str, subject_id: int, thumbnail_img_url: str | None) -> Exam:
    with transaction.atomic():
        subject = Subject.objects.filter(id=subject_id).first()
        if not subject:
            raise_error(ErrorMessages.SUBJECT_NOT_FOUND)

        exam, created = Exam.objects.get_or_create(
            title=title,
            defaults={
                "subject": subject,
                **({"thumbnail_img_url": thumbnail_img_url} if thumbnail_img_url else {}),
            },
        )
        if not created:
            raise_error(ErrorMessages.EXAM_CONFLICT)
        return exam
