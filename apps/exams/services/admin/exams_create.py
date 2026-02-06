from __future__ import annotations

import os
from uuid import uuid4

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from apps.courses.models.subjects import Subject
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models.exams import Exam


def _store_thumbnail(thumbnail_img: UploadedFile) -> tuple[str, str]:
    name = thumbnail_img.name or "thumbnail"
    _, ext = os.path.splitext(name)
    ext = ext.lower() if ext else ".png"
    filename = f"exams/{uuid4().hex}{ext}"
    saved_path = default_storage.save(filename, thumbnail_img)
    return saved_path, default_storage.url(saved_path)


def create_exam(title: str, subject_id: int, thumbnail_img: UploadedFile | None) -> Exam:
    with transaction.atomic():
        subject = Subject.objects.filter(id=subject_id).first()
        if not subject:
            raise_error(ErrorMessages.SUBJECT_NOT_FOUND)

        saved_path = None
        thumbnail_img_url = None
        if thumbnail_img is not None:
            saved_path, thumbnail_img_url = _store_thumbnail(thumbnail_img)
        try:
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
        except Exception:
            if saved_path:
                default_storage.delete(saved_path)
            raise
