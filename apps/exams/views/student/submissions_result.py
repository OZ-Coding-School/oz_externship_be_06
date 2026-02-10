from typing import cast

from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from apps.exams.constants import ErrorMessages
from apps.exams.models import ExamSubmission
from apps.exams.schemas.student import exam_submission_detail_schema
from apps.exams.serializers.student.submissions_result import ExamSubmissionSerializer
from apps.exams.services.student.submissions_result import get_exam_submission_detail
from apps.exams.validators import parse_positive_int
from apps.exams.views.mixins import ExamsExceptionMixin


@exam_submission_detail_schema
class ExamSubmissionDetailView(ExamsExceptionMixin, RetrieveAPIView[ExamSubmission]):
    # 시험 제출 결과 상세 조회
    permission_classes = [IsAuthenticated]
    serializer_class = ExamSubmissionSerializer

    def get_object(self) -> ExamSubmission:
        submission_id = parse_positive_int(self.kwargs.get("submission_id"), ErrorMessages.INVALID_EXAM_SESSION)
        user_id = cast(int, self.request.user.id)

        return get_exam_submission_detail(
            submission_id=submission_id,
            user_id=user_id,
        )
