from django.db import transaction

from apps.exams.models import Exam
from apps.exams.constants import ErrorMessages
from apps.courses.models import Subject


@transaction.atomic
def update_exam(
    *,
    exam_id: int,
    title: str,
    subject: Subject,   # serializer가 조회한 subject_id의 인스턴스
    thumbnail_img_url: str | None = None,
) -> Exam:

    # 시험 조회 (404)
    # 한 시험을 2명이 동시에 수정할 때, 한명이 끝날 때까지 대기
    try:
        exam = Exam.objects.select_for_update().get(id=exam_id)
    except Exam.DoesNotExist:
        raise Exception(ErrorMessages.EXAM_UPDATE_NOT_FOUND.value)

    # 기본 필드 수정
    exam.title = title
    exam.subject = subject

    # 썸네일 처리
    if thumbnail_img_url is not None:
        exam.thumbnail_img_url = thumbnail_img_url

    # 저장
    exam.save()

    return exam
