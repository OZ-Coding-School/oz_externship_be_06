from __future__ import annotations

from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import Exam, ExamQuestion


def get_exam_detail_or_error(*, exam_id: int) -> Exam:
    if exam_id <= 0:
        raise_error(ErrorMessages.INVALID_EXAM_LIST_REQUEST)

    try:
        exam = get_object_or_404(
            Exam.objects.select_related("subject").prefetch_related(
                Prefetch("questions", queryset=ExamQuestion.objects.all())
            ),
            id=exam_id,
        )
    except Http404:
        raise_error(ErrorMessages.EXAM_NOT_FOUND)

    return exam
