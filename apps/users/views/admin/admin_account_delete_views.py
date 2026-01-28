from typing import NoReturn

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsAdmin
from apps.users.services.admin_account_delete_service import (
    AccountNotFoundError,
    delete_account,
)

#어드민 회원정보 삭제 api
class AdminAccountDeleteAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied(detail="권한이 없습니다.")

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 회원 정보 삭제 API",
        description="""
        관리자(ADMIN)가 회원 정보를 삭제합니다.
        삭제 시 해당 유저와 관련된 모든 데이터가 즉시 삭제되며 되돌릴 수 없습니다.
        """,
        parameters=[
            OpenApiParameter(
                name="account_id",
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
                description="삭제할 회원 ID",
            ),
        ],
        responses={
            200: OpenApiResponse(description="유저 데이터가 삭제되었습니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="사용자 정보를 찾을 수 없습니다."),
        },
    )
    def delete(self, request: Request, account_id: int) -> Response:
        try:
            deleted_id = delete_account(account_id)
        except AccountNotFoundError:
            return Response(
                {"error_detail": "사용자 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"detail": f"유저 데이터가 삭제되었습니다. - pk: {deleted_id}"},
            status=status.HTTP_200_OK,
        )
