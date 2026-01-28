from typing import Any

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ErrorMessages
from apps.exams.serializers.admin.exams_create import (
    AdminExamCreateRequestSerializer,
    AdminExamCreateResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.views.admin.exams_create import AdminExamCreateAPIView
from apps.exams.views.admin.exams_list import AdminExamListView


class AdminExamRouterAPIView(APIView):

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
                enum=["created_at", "updated_at", "title"],
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
                response=ErrorResponseSerializer,
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 조회 요청",
                        value={"error_detail": ErrorMessages.INVALID_EXAM_LIST_REQUEST.value},
                    )
                ],
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        "인증 실패",
                        value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                    )
                ],
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        "권한 없음",
                        value={"error_detail": ErrorMessages.NO_EXAM_LIST_PERMISSION.value},
                    )
                ],
            ),
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return AdminExamListView.as_view()(request._request, *args, **kwargs)

    @extend_schema(
        tags=["admin_exams"],
        summary="관리자 쪽지시험 생성 API",
        description="""
            관리자/스태프 권한으로 쪽지시험을 생성합니다.
            """,
        request=AdminExamCreateRequestSerializer,
        responses={
            201: AdminExamCreateResponseSerializer,
            400: OpenApiResponse(ErrorResponseSerializer, description="유효하지 않은 시험 생성 요청"),
            401: OpenApiResponse(ErrorResponseSerializer, description="인증 실패"),
            403: OpenApiResponse(ErrorResponseSerializer, description="쪽지시험 생성 권한 없음"),
            404: OpenApiResponse(ErrorResponseSerializer, description="과목 정보 없음"),
            409: OpenApiResponse(ErrorResponseSerializer, description="동일한 이름의 시험 존재"),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return AdminExamCreateAPIView.as_view()(request._request, *args, **kwargs)
