from django.db.models import QuerySet
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.utils.pagination import AdminExamPagination
from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam
from apps.exams.permissions import IsExamStaff
from apps.exams.serializers.admin_exam_list import AdminExamListItemSerializer
from apps.exams.serializers.error import ErrorDetailSerializer
from apps.exams.services.admin_exam_list import (
    AdminExamListService,
    InvalidAdminExamListParams,
)


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
            response=ErrorDetailSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 조회 요청", value={"error_detail": ErrorMessages.INVALID_EXAM_LIST_REQUEST}
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorDetailSerializer,
            description="Unauthorized",
            examples=[OpenApiExample("인증 실패", value={"error_detail": ErrorMessages.UNAUTHORIZED})],
        ),
        403: OpenApiResponse(
            response=ErrorDetailSerializer,
            description="Forbidden",
            examples=[OpenApiExample("권한 없음", value={"error_detail": ErrorMessages.NO_EXAM_LIST_PERMISSION})],
        ),
    },
)
class AdminExamListView(ListAPIView[Exam]):
    permission_classes = [IsAuthenticated, IsExamStaff]
    serializer_class = AdminExamListItemSerializer
    pagination_class = AdminExamPagination

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"error_detail": ErrorMessages.UNAUTHORIZED},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if isinstance(exc, PermissionDenied):
            return Response(
                {"error_detail": ErrorMessages.NO_EXAM_LIST_PERMISSION},
                status=status.HTTP_403_FORBIDDEN,
            )
        if isinstance(exc, InvalidAdminExamListParams):
            return Response(
                {"error_detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().handle_exception(exc)

    def get_queryset(self) -> QuerySet[Exam]:
        qp = self.request.query_params

        params = AdminExamListService.parse_params(
            search_keyword=qp.get("search_keyword"),
            subject_id=qp.get("subject_id"),
            sort=qp.get("sort"),
            order=qp.get("order"),
        )
        return AdminExamListService.get_queryset(params)
