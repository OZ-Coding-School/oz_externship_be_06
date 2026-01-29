from typing import NoReturn

from django.db.models import QuerySet
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from apps.core.utils.pagination import AdminExamPagination
from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import Exam
from apps.exams.permissions import IsExamStaff
from apps.exams.serializers.admin.exams_list import AdminExamListItemSerializer
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin.exams_list import (
    AdminExamListService,
    InvalidAdminExamListParams,
)
from apps.exams.views.mixins import ExamsExceptionMixin


@extend_schema(
    tags=["admin_exams"],
    summary="어드민 시험 목록 조회",
    description="어드민 시험 목록을 페이지네이션/검색/과목필터/정렬로 조회합니다.",
    parameters=[
        OpenApiParameter(name="page", required=False, type=int, description="페이지(1부터)"),
        OpenApiParameter(name="size", required=False, type=int, description="페이지 크기"),
        OpenApiParameter(name="search_keyword", required=False, type=str, description="검색어(시험 제목)"),
        OpenApiParameter(name="subject_id", required=False, type=int, description="과목 ID"),
        OpenApiParameter(name="sort", required=False, type=str, description="정렬 기준", enum=["created_at", "title"]),
        OpenApiParameter(name="order", required=False, type=str, description="정렬 방향", enum=["asc", "desc"]),
    ],
    responses={
        200: OpenApiResponse(description="OK"),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 조회 요청", value={"error_detail": ErrorMessages.INVALID_EXAM_LIST_REQUEST.value}
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[OpenApiExample("인증 실패", value={"error_detail": ErrorMessages.UNAUTHORIZED.value})],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[OpenApiExample("권한 없음", value={"error_detail": ErrorMessages.NO_EXAM_LIST_PERMISSION.value})],
        ),
    },
)
class AdminExamListView(ExamsExceptionMixin, ListAPIView[Exam]):
    permission_classes = [IsAuthenticated, IsExamStaff]
    serializer_class = AdminExamListItemSerializer
    pagination_class = AdminExamPagination

    def permission_denied(
        self,
        request: Request,
        message: str | None = None,
        code: str | None = None,
    ) -> NoReturn:
        from rest_framework.exceptions import NotAuthenticated, PermissionDenied

        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=ErrorMessages.NO_EXAM_LIST_PERMISSION.value)

    def get_queryset(self) -> QuerySet[Exam]:
        qp = self.request.query_params

        try:
            params = AdminExamListService.parse_params(
                search_keyword=qp.get("search_keyword"),
                subject_id=qp.get("subject_id"),
                sort=qp.get("sort"),
                order=qp.get("order"),
            )
        except InvalidAdminExamListParams as exc:
            raise ErrorDetailException(str(exc), status.HTTP_400_BAD_REQUEST) from exc
        return AdminExamListService.get_queryset(params)
