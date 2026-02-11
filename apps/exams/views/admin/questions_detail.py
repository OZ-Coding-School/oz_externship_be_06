from typing import NoReturn

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers.error import ErrorResponseSerializer
from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models import ExamQuestion
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
from apps.exams.services.admin.questions_update import update_exam_question
from apps.exams.validators import parse_positive_int
from apps.exams.views.mixins import ExamsExceptionMixin


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
    @extend_schema(
        tags=["admin_exams"],
        summary="어드민 문제 삭제",
        description="쪽지시험 문제를 삭제합니다.",
        responses={
            200: AdminExamQuestionDeleteResponseSerializer,
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 문제 삭제 요청",
                        value={"error_detail": ErrorMessages.INVALID_QUESTION_DELETE_REQUEST.value},
                    ),
                ],
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        "인증 실패",
                        value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                    ),
                ],
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        "권한 없음",
                        value={"error_detail": ErrorMessages.NO_QUESTION_DELETE_PERMISSION.value},
                    ),
                ],
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Not Found",
                examples=[
                    OpenApiExample(
                        "문제 정보 없음",
                        value={"error_detail": ErrorMessages.QUESTION_NOT_FOUND.value},
                    ),
                ],
            ),
            409: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Conflict",
                examples=[
                    OpenApiExample(
                        "문제 삭제 충돌",
                        value={"error_detail": ErrorMessages.QUESTION_DELETE_CONFLICT.value},
                    ),
                ],
            ),
        },
    )
    def delete(self, request: Request, question_id: int) -> Response:
        parse_positive_int(question_id, ErrorMessages.INVALID_QUESTION_DELETE_REQUEST)

        result = delete_exam_question(question_id)

        serializer = self.serializer_class(data=result)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["admin_exams"],
        summary="쪽지시험 문제 수정 API",
        description="관리자/스태프가 쪽지시험 문제를 수정합니다.",
        request=AdminExamQuestionUpdateRequestSerializer,
        responses={
            200: AdminExamQuestionUpdateResponseSerializer,
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 문제 수정 데이터",
                        value={"error_detail": ErrorMessages.INVALID_QUESTION_UPDATE_REQUEST.value},
                    ),
                ],
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        "인증 실패",
                        value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                    ),
                ],
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        "권한 없음",
                        value={"error_detail": ErrorMessages.NO_QUESTION_UPDATE_PERMISSION.value},
                    ),
                ],
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Not Found",
                examples=[
                    OpenApiExample(
                        "문제 정보 찾을 수 없음",
                        value={"error_detail": ErrorMessages.QUESTION_UPDATE_NOT_FOUND.value},
                    ),
                ],
            ),
            409: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Conflict",
                examples=[
                    OpenApiExample(
                        "문제 수 제한 또는 총 배점을 초과하여 문제를 수정할 수 없음",
                        value={"error_detail": ErrorMessages.QUESTION_UPDATE_CONFLICT.value},
                    ),
                ],
            ),
        },
    )
    def put(self, request: Request, question_id: int) -> Response:
        parse_positive_int(question_id, ErrorMessages.INVALID_QUESTION_UPDATE_REQUEST)
        # 1.문제 조회
        try:
            question = ExamQuestion.objects.get(id=question_id)
        except ExamQuestion.DoesNotExist:
            raise_error(ErrorMessages.QUESTION_UPDATE_NOT_FOUND)

        # 2.Serializer 검증
        serializer = AdminExamQuestionUpdateRequestSerializer(
            instance=question,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            raise_error(ErrorMessages.INVALID_QUESTION_UPDATE_REQUEST)

        update_data = serializer.validated_data

        # 3.Service 호출
        updated_question = update_exam_question(
            instance=question,
            update_data=update_data,
        )

        # 4.응답
        response_serializer = AdminExamQuestionUpdateResponseSerializer(updated_question)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
