from typing import NoReturn

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsAdminStaff
from apps.users.serializers.admin.admin_account_serializers import (
    AdminAccountUpdateRequestSerializer,
    AdminAccountUpdateResponseSerializer,
)
from apps.users.services.admin_account_service import (
    AccountNotFoundError,
    AccountUpdateConflictError,
    update_account,
)


# 어드민 회원 정보 수정
class AdminAccountUpdateAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminStaff]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied(detail="권한이 없습니다.")

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 회원 정보 수정 API",
        description="""
        스태프(조교, 러닝코치, 운영매니저) 또는 관리자가 회원 정보를 수정합니다.
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
        request=AdminAccountUpdateRequestSerializer,
        responses={
            200: AdminAccountUpdateResponseSerializer,
            400: OpenApiResponse(description="유효하지 않은 요청입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="사용자 정보를 찾을 수 없습니다."),
            409: OpenApiResponse(description="휴대폰 번호 중복으로 인하여 요청 처리에 실패하였습니다."),
        },
    )
    def patch(self, request: Request, account_id: int) -> Response:
        serializer = AdminAccountUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data
        if not validated_data:
            return Response(
                {"error_detail": "수정할 항목이 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = update_account(account_id, validated_data)
        except AccountNotFoundError:
            return Response(
                {"error_detail": "사용자 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except AccountUpdateConflictError as e:
            return Response(
                {"error_detail": e.message},
                status=status.HTTP_409_CONFLICT,
            )

        response_serializer = AdminAccountUpdateResponseSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
