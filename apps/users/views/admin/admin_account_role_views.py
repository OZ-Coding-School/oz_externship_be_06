from typing import NoReturn

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsAdmin
from apps.users.serializers.admin.admin_account_role_serializers import (
    AdminAccountRoleUpdateSerializer,
)
from apps.users.services.admin_account_role_service import (
    AccountNotFoundError,
    update_account_role,
)


# 어드민 권한 변경 api
class AdminAccountRoleUpdateAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied(detail="권한이 없습니다.")

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 권한 변경 API",
        description="""
        관리자(ADMIN)가 회원의 권한을 변경합니다.

        - USER, ADMIN: role만 전달
        - TA, STUDENT: role과 cohort_id 필수
        - LC, OM: role과 assigned_courses 필수
        """,
        parameters=[
            OpenApiParameter(
                name="account_id",
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
                description="회원 ID",
            ),
        ],
        request=AdminAccountRoleUpdateSerializer,
        responses={
            200: OpenApiResponse(description="권한이 변경되었습니다."),
            400: OpenApiResponse(description="잘못된 요청"),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="사용자 정보를 찾을 수 없습니다."),
        },
    )
    def patch(self, request: Request, account_id: int) -> Response:
        serializer = AdminAccountRoleUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data

        try:
            update_account_role(
                account_id=account_id,
                role=validated_data["role"],
                cohort=validated_data.get("cohort_id"),
                assigned_courses=validated_data.get("assigned_courses"),
            )
        except AccountNotFoundError:
            return Response(
                {"error_detail": "사용자 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"detail": "권한이 변경되었습니다."},
            status=status.HTTP_200_OK,
        )
