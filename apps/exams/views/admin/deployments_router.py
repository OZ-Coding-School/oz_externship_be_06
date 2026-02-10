from __future__ import annotations

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

from apps.core.serializers.error import ErrorResponseSerializer
from apps.exams.constants import ErrorMessages
from apps.exams.serializers.admin.deployments_create import (
    AdminExamDeploymentCreateRequestSerializer,
    AdminExamDeploymentCreateResponseSerializer,
)
from apps.exams.views.admin.deployments_create import (
    AdminExamDeploymentCreateAPIView,
)
from apps.exams.views.admin.deployments_list import (
    AdminExamDeploymentListAPIView,
)
from apps.exams.views.mixins import ExamsExceptionMixin


class AdminExamDeploymentRouterAPIView(ExamsExceptionMixin, APIView):
    @extend_schema(
        tags=["admin_exams"],
        summary="어드민 배포 목록 조회",
        description="쪽지시험 배포 내역을 페이지네이션/검색/필터/정렬로 조회합니다.",
        parameters=[
            OpenApiParameter(name="page", required=False, type=int, description="페이지(1부터)"),
            OpenApiParameter(name="size", required=False, type=int, description="페이지 크기"),
            OpenApiParameter(name="search_keyword", required=False, type=str, description="검색어(시험 제목)"),
            OpenApiParameter(name="subject_id", required=False, type=int, description="과목 ID"),
            OpenApiParameter(name="cohort_id", required=False, type=int, description="기수 ID"),
            OpenApiParameter(
                name="sort",
                required=False,
                type=str,
                description="정렬 기준",
                enum=["created_at", "submit_count", "avg_score"],
            ),
            OpenApiParameter(name="order", required=False, type=str, description="정렬 방향", enum=["asc", "desc"]),
        ],
        responses={
            200: OpenApiResponse(description="OK"),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 조회 요청",
                        value={"error_detail": ErrorMessages.INVALID_DEPLOYMENT_LIST_REQUEST.value},
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
                examples=[
                    OpenApiExample(
                        "권한 없음",
                        value={"error_detail": ErrorMessages.NO_DEPLOYMENT_LIST_PERMISSION.value},
                    )
                ],
            ),
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return AdminExamDeploymentListAPIView.as_view()(request._request, *args, **kwargs)

    @extend_schema(
        tags=["admin_exams"],
        summary="어드민 배포 생성",
        description="쪽지시험 배포를 생성합니다.",
        request=AdminExamDeploymentCreateRequestSerializer,
        responses={
            201: AdminExamDeploymentCreateResponseSerializer,
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 배포 생성 요청",
                        value={"error_detail": ErrorMessages.INVALID_DEPLOYMENT_CREATE_REQUEST.value},
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
                        value={"error_detail": ErrorMessages.NO_DEPLOYMENT_CREATE_PERMISSION.value},
                    )
                ],
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Not Found",
                examples=[
                    OpenApiExample(
                        "배포 대상 없음",
                        value={"error_detail": ErrorMessages.DEPLOYMENT_TARGET_NOT_FOUND.value},
                    )
                ],
            ),
            409: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Conflict",
                examples=[
                    OpenApiExample(
                        "중복 배포",
                        value={"error_detail": ErrorMessages.DUPLICATE_DEPLOYMENT.value},
                    )
                ],
            ),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return AdminExamDeploymentCreateAPIView.as_view()(request._request, *args, **kwargs)
