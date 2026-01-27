from typing import Any

from django.db.models import Count, Q, QuerySet
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
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.utils.pagination import AdminExamPagination
from apps.exams.models import Exam
from apps.exams.permissions import IsExamStaff
from apps.exams.serializers.admin_exam_list import AdminExamListItemSerializer
from apps.exams.serializers.error import ErrorDetailSerializer


@extend_schema(
    tags=["admin_exams"],
    summary="어드민 시험 목록 조회",
    description="어드민 시험 목록을 페이지네이션/검색/과목필터/정렬로 조회합니다.",
    parameters=[
        OpenApiParameter(name="page", required=False, type=int, description="페이지(1부터)"),
        OpenApiParameter(name="size", required=False, type=int, description="페이지 크기"),
        OpenApiParameter(name="search_keyword", required=False, type=str, description="검색어(시험 제목)"),
        OpenApiParameter(name="subject_id", required=False, type=int, description="과목 ID"),
        OpenApiParameter(
            name="sort",
            required=False,
            type=str,
            description="정렬 기준",
            enum=["created_at", "title"],
        ),
        OpenApiParameter(
            name="order",
            required=False,
            type=str,
            description="정렬 방향",
            enum=["asc", "desc"],
        ),
    ],
    responses={
        200: OpenApiResponse(description="OK"),
        400: OpenApiResponse(
            response=ErrorDetailSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 조회 요청",
                    value={"error_detail": "유효하지 않은 조회 요청입니다."},
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorDetailSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": "자격 인증 데이터가 제공되지 않았습니다."},
                )
            ],
        ),
        403: OpenApiResponse(
            response=ErrorDetailSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": "쪽지시험 목록 조회 권한이 없습니다."},
                )
            ],
        ),
    },
)
class AdminExamListView(ListAPIView[Exam]):
    permission_classes = [IsAuthenticated, IsExamStaff]
    serializer_class = AdminExamListItemSerializer
    pagination_class = AdminExamPagination

    ALLOWED_SORT = {"created_at", "title"}
    ALLOWED_ORDER = {"asc", "desc"}
    DEFAULT_SORT = "created_at"
    DEFAULT_ORDER = "desc"

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if isinstance(exc, PermissionDenied):
            return Response(
                {"error_detail": "쪽지시험 목록 조회 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().handle_exception(exc)

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        sort = request.query_params.get("sort") or self.DEFAULT_SORT
        order = request.query_params.get("order") or self.DEFAULT_ORDER

        if sort not in self.ALLOWED_SORT or order not in self.ALLOWED_ORDER:
            return Response(
                {"error_detail": "유효하지 않은 조회 요청입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().list(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Exam]:
        qp = self.request.query_params

        search_keyword = qp.get("search_keyword")
        subject_id = qp.get("subject_id")

        qs = Exam.objects.select_related("subject").annotate(
            question_count=Count("questions", distinct=True),
            submit_count=Count("deployments__submissions", distinct=True),
        )

        if search_keyword:
            qs = qs.filter(Q(title__icontains=search_keyword))

        if subject_id:
            qs = qs.filter(subject_id=subject_id)

        sort = qp.get("sort") or self.DEFAULT_SORT
        order = qp.get("order") or self.DEFAULT_ORDER
        prefix = "-" if order == "desc" else ""
        return qs.order_by(f"{prefix}{sort}")
