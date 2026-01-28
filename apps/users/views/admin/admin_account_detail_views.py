from typing import NoReturn

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.permissions import IsAdminStaff
from apps.users.serializers.admin.admin_account_detail_serializers import (
    AdminAccountDetailResponseSerializer,
)


# 어드민 회원 정보 상세 조회
class AdminAccountDetailAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminStaff]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied(detail="권한이 없습니다.")

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 회원 정보 상세 조회 API",
        description="""
        스태프(조교, 러닝코치, 운영매니저) 또는 관리자가 회원 상세 정보를 조회합니다.

        조회 대상 회원의 권한에 따라 반환되는 assigned_courses 내용이 다릅니다:
        - 조교(TA): 담당 기수 목록 (과정명, 기수, 상태)
        - 러닝코치(LC), 운영매니저(OM): 담당 과정 목록 (과정명)
        - 수강생(STUDENT): 수강 기수 목록 (과정명, 기수, 상태)
        - 그 외: 빈 배열
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
        responses={
            200: OpenApiResponse(description="회원 상세 정보"),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="사용자 정보를 찾을 수 없습니다."),
        },
    )
    def get(self, request: Request, account_id: int) -> Response:
        try:
            user = User.objects.get(id=account_id)
        except User.DoesNotExist:
            return Response(
                {"error_detail": "사용자 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminAccountDetailResponseSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
