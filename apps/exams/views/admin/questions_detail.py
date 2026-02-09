from typing import NoReturn

from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import ExamQuestion
from apps.exams.schemas.admin import (
    admin_exam_question_delete_schema,
    admin_exam_question_update_schema,
)
from apps.exams.serializers.admin.questions_delete import (
    AdminExamQuestionDeleteResponseSerializer,
)
from apps.exams.serializers.admin.questions_update import (
    AdminExamQuestionUpdateRequestSerializer,
    AdminExamQuestionUpdateResponseSerializer,
)
from apps.exams.services.admin.questions_delete import (
    delete_exam_question,
)
from apps.exams.services.admin.questions_update import (
    BusinessRuleError,
    ConflictRuleError,
    update_exam_question,
)
from apps.exams.views.mixins import ExamsExceptionMixin


# 어드민 문제 삭제 / 쪽지시험 문제 수정 API
class AdminExamQuestionDetailAPIView(ExamsExceptionMixin, APIView):
    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = AdminExamQuestionDeleteResponseSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail=ErrorMessages.UNAUTHORIZED.value)

        if request.method == "PUT":
            raise PermissionDenied(detail=ErrorMessages.NO_QUESTION_UPDATE_PERMISSION.value)
        elif request.method == "DELETE":
            raise PermissionDenied(detail=ErrorMessages.NO_QUESTION_DELETE_PERMISSION.value)
        else:
            raise PermissionDenied()

    # delete
    @admin_exam_question_delete_schema
    def delete(self, request: Request, question_id: int) -> Response:
        if question_id <= 0:
            raise_error(ErrorMessages.INVALID_QUESTION_DELETE_REQUEST)

        result = delete_exam_question(question_id)

        serializer = self.serializer_class(data=result)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @admin_exam_question_update_schema
    def put(self, request: Request, question_id: int) -> Response:
        # 1.문제 조회
        try:
            question = ExamQuestion.objects.get(id=question_id)
        except ExamQuestion.DoesNotExist:
            return Response(
                {"error_detail": ErrorMessages.QUESTION_UPDATE_NOT_FOUND.value},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2.Serializer 검증
        serializer = AdminExamQuestionUpdateRequestSerializer(
            instance=question,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        update_data = serializer.validated_data

        # 3.Service 호출
        try:
            updated_question = update_exam_question(
                instance=question,
                update_data=update_data,
            )
        # 409
        except ConflictRuleError:
            return Response(
                {"error_detail": ErrorMessages.QUESTION_UPDATE_CONFLICT.value},
                status=status.HTTP_409_CONFLICT,
            )
        # BusinessRuleError를 다 400으로 반환
        except BusinessRuleError:
            return Response(
                {"error_detail": ErrorMessages.INVALID_QUESTION_UPDATE_REQUEST.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 4.응답
        response_serializer = AdminExamQuestionUpdateResponseSerializer(updated_question)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
