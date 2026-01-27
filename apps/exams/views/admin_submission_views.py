from __future__ import annotations

from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.pagination import SimplePagePagination
from apps.exams.models import ExamSubmission
from apps.exams.permissions import IsExamStaff
from apps.exams.serializers.admin_submission_serializers import (
    AdminExamSubmissionListResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer


class AdminExamSubmissionListAPIView(APIView):
    """어드민 쪽지시험 응시 내역 목록 조회 API."""

    permission_classes = [IsAuthenticated, IsExamStaff]
    pagination_class = SimplePagePagination

    @extend_schema(
        tags=["admin_exams"],
        summary="특정시험 응시 내역 목록 조회 API",
        description="""
        스태프(조교, 러닝 코치, 운영매니저), 관리자 권한을 가진 유저가
        쪽지시험 응시 내역 목록을 조회합니다.
        """,
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="페이지 번호",
                required=False,
            ),
            OpenApiParameter(
                name="size",
                type=int,
                location=OpenApiParameter.QUERY,
                description="페이지 크기",
                required=False,
            ),
            OpenApiParameter(
                name="search_keyword",
                type=str,
                location=OpenApiParameter.QUERY,
                description="검색 키워드 (닉네임, 이름)",
                required=False,
            ),
            OpenApiParameter(
                name="cohort_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="기수 ID",
                required=False,
            ),
            OpenApiParameter(
                name="exam_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="시험 ID",
                required=False,
            ),
            OpenApiParameter(
                name="sort",
                type=str,
                location=OpenApiParameter.QUERY,
                description="정렬 기준 (score, started_at)",
                required=False,
            ),
            OpenApiParameter(
                name="order",
                type=str,
                location=OpenApiParameter.QUERY,
                description="정렬 순서 (asc, desc)",
                required=False,
            ),
        ],
        responses={
            200: AdminExamSubmissionListResponseSerializer(many=True),
            400: OpenApiResponse(ErrorResponseSerializer, description="유효하지 않은 조회 요청"),
            401: OpenApiResponse(ErrorResponseSerializer, description="자격 인증 데이터가 제공되지 않았습니다"),
            403: OpenApiResponse(ErrorResponseSerializer, description="특정시험 응시 내역 조회 권한이 없습니다"),
            404: OpenApiResponse(ErrorResponseSerializer, description="조회된 응시 내역이 없습니다"),
        },
    )
    def get(self, request: Request) -> Response:
        # Query parameters
        search_keyword = request.query_params.get("search_keyword", "")
        cohort_id = request.query_params.get("cohort_id")
        exam_id = request.query_params.get("exam_id")
        sort = request.query_params.get("sort", "started_at")
        order = request.query_params.get("order", "desc")

        # QuerySet 생성
        queryset = ExamSubmission.objects.select_related(
            "submitter",
            "deployment",
            "deployment__exam",
            "deployment__exam__subject",
            "deployment__cohort",
            "deployment__cohort__course",
        ).all()

        # 필터링: 검색 키워드
        if search_keyword:
            queryset = queryset.filter(
                Q(submitter__nickname__icontains=search_keyword) | Q(submitter__name__icontains=search_keyword)
            )

        # 필터링: 기수 ID
        if cohort_id:
            try:
                cohort_id_int = int(cohort_id)
                queryset = queryset.filter(deployment__cohort_id=cohort_id_int)
            except ValueError:
                return Response(
                    {"error_detail": "유효하지 않은 조회 요청입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # 필터링: 시험 ID
        if exam_id:
            try:
                exam_id_int = int(exam_id)
                queryset = queryset.filter(deployment__exam_id=exam_id_int)
            except ValueError:
                return Response(
                    {"error_detail": "유효하지 않은 조회 요청입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # 정렬
        valid_sort_fields = ["score", "started_at"]
        if sort not in valid_sort_fields:
            sort = "started_at"

        if order == "asc":
            sort_field = sort
        else:  # desc (기본값)
            sort_field = f"-{sort}"

        queryset = queryset.order_by(sort_field)

        # 결과가 비어있을 경우 404 반환
        if not queryset.exists():
            return Response(
                {"error_detail": "조회된 응시 내역이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 페이지네이션
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        if paginated_queryset is None:
            paginated_queryset = []

        # Serializer를 사용하여 응답 데이터 생성
        serializer = AdminExamSubmissionListResponseSerializer(paginated_queryset, many=True)

        # 페이지네이션 응답 생성
        response = paginator.get_paginated_response(serializer.data)

        return response
