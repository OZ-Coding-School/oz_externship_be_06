from typing import NoReturn

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsAdminStaff
from apps.users.serializers.admin.admin_withdrawal_serializers import (
    AdminWithdrawalCancelSerializer,
    AdminWithdrawalDetailSerializer,
    AdminWithdrawalListSerializer,
)
from apps.users.services.admin_withdrawal_service import (
    WithdrawalNotFoundError,
    cancel_withdrawal,
    get_withdrawal_detail,
    get_withdrawal_list,
)
from apps.users.utils.pagination import AdminListPagination


# 어드민 탈퇴 내역 목록 조회 api
class AdminWithdrawalListAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminStaff]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied(detail="권한이 없습니다.")

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 회원 탈퇴 내역 목록 조회 API",
        description="""
        스태프(조교, 러닝코치, 운영매니저) 또는 관리자가 회원 탈퇴 내역 목록을 조회합니다.

        페이지네이션, 검색, 필터링, 정렬 기능을 제공합니다.
        기본적으로 ID 순으로 정렬됩니다.
        """,
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="페이지 번호",
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="페이지 크기 (기본: 10, 최대: 100)",
            ),
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="검색어 (이메일, 이름)",
            ),
            OpenApiParameter(
                name="role",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="권한 필터",
                enum=[
                    "user",
                    "training_assistant",
                    "operation_manager",
                    "learning_coach",
                    "admin",
                    "student",
                ],
            ),
            OpenApiParameter(
                name="sort",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="정렬 기준 (latest: 최신순, oldest: 오래된순, 기본: ID순)",
                enum=["latest", "oldest"],
            ),
        ],
        responses={
            200: AdminWithdrawalListSerializer(many=True),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
        },
    )
    def get(self, request: Request) -> Response:
        search = request.query_params.get("search")
        role = request.query_params.get("role")
        sort = request.query_params.get("sort")

        queryset = get_withdrawal_list(search=search, role=role, sort=sort)

        paginator = AdminListPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = AdminWithdrawalListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = AdminWithdrawalListSerializer(queryset, many=True)
        return Response(serializer.data)


# 어드민 탈퇴 내역 상세 조회 api
class AdminWithdrawalDetailAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminStaff]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied(detail="권한이 없습니다.")

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 회원 탈퇴 내역 상세 조회 API",
        description="""
        스태프(조교, 러닝코치, 운영매니저) 또는 관리자가 회원 탈퇴 내역 상세 정보를 조회합니다.

        유저의 권한에 따라 담당/수강 과정 정보가 포함됩니다:
        - 수강생: 수강 과정-기수
        - 조교: 담당 과정-기수
        - 운영매니저, 러닝코치: 담당 과정 목록
        """,
        parameters=[
            OpenApiParameter(
                name="withdrawal_id",
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
                description="탈퇴 내역 ID",
            ),
        ],
        responses={
            200: AdminWithdrawalDetailSerializer,
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="회원탈퇴 정보를 찾을 수 없습니다."),
        },
    )
    def get(self, request: Request, withdrawal_id: int) -> Response:
        try:
            withdrawal = get_withdrawal_detail(withdrawal_id)
        except WithdrawalNotFoundError:
            return Response(
                {"error_detail": "회원탈퇴 정보를 찾을 수 없습니다."},
                status=404,
            )

        serializer = AdminWithdrawalDetailSerializer(withdrawal)
        return Response(serializer.data)

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 탈퇴 취소 API",
        description="""
        스태프(조교, 러닝코치, 운영매니저) 또는 관리자가 회원 탈퇴를 취소합니다.

        해당 유저의 탈퇴요청은 삭제되며 해당 유저는 즉시 이용가능한 상태로 복구됩니다.
        """,
        parameters=[
            OpenApiParameter(
                name="withdrawal_id",
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
                description="탈퇴 내역 ID",
            ),
        ],
        responses={
            200: AdminWithdrawalCancelSerializer,
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="회원탈퇴 정보를 찾을 수 없습니다."),
        },
    )
    def delete(self, request: Request, withdrawal_id: int) -> Response:
        try:
            cancel_withdrawal(withdrawal_id)
        except WithdrawalNotFoundError:
            return Response(
                {"error_detail": "회원탈퇴 정보를 찾을 수 없습니다."},
                status=404,
            )

        serializer = AdminWithdrawalCancelSerializer({"detail": "회원 탈퇴 취소처리 완료."})
        return Response(serializer.data, status=200)
