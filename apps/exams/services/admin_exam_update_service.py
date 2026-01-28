from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.exams.models import Exam
from apps.exams.exceptions import (
    ExamNotFoundError,
)
from apps.core.utils.s3 import S3Uploader
from apps.courses.models import Subject


@transaction.atomic
def update_exam(
    *,
    exam_id: int,
    title: str,
    subject: Subject,   # serializer가 조회한 subject_id의 인스턴스
    thumbnail_img=None,
) -> Exam:

    #  시험 조회 (404)
    try:
        exam = Exam.objects.select_for_update().get(id=exam_id)
    except Exam.DoesNotExist:
        raise ExamNotFoundError()

    # 기본 필드 수정
    exam.title = title
    exam.subject = subject

    # 썸네일 수정 (있는 경우만)
    if thumbnail_img:
        uploader = S3Uploader()
        thumbnail_url = uploader.upload(
            file=thumbnail_img,
            folder="exams"
        )
        exam.thumbnail_img_url = thumbnail_url

    # 저장
    exam.save()

    return exam
