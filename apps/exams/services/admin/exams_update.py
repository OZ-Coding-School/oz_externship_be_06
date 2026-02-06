from django.db import transaction
from rest_framework import status

from apps.courses.models import Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam
from apps.exams.exceptions import ErrorDetailException

@transaction.atomic
def update_exam(
    *,
    exam_id: int,
    title: str | None = None,
    subject: Subject | None = None,
    thumbnail_img_url: str | None = None,
) -> Exam:

    # 시험 조회 (404)
    # 한 시험을 2명이 동시에 수정할 때, 한명이 끝날 때까지 대기
    try:
        exam = Exam.objects.select_for_update().get(id=exam_id)
    except Exam.DoesNotExist:
        raise ErrorDetailException(
            ErrorMessages.EXAM_UPDATE_NOT_FOUND.value,
            status.HTTP_404_NOT_FOUND,
        )

    # 409
    if title is not None:
        if Exam.objects.filter(title=title).exclude(id=exam.id).exists():
            raise ErrorDetailException(
                ErrorMessages.EXAM_UPDATE_CONFLICT.value,
                status.HTTP_409_CONFLICT,
            )
        exam.title = title

    if subject is not None:
        exam.subject = subject

    # title, subject 수정없이 thumbnail만 수정할 경우
    if thumbnail_img_url is not None:
        exam.thumbnail_img_url = thumbnail_img_url

    # 저장
    exam.save()

    return exam
