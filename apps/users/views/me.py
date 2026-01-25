from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.me import (
    MeResponseSerializer,
    MeUpdateRequestSerializer,
    MeUpdateResponseSerializer,
)
from apps.users.services.me_service import update_user_profile


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="내 정보 조회",
        responses=MeResponseSerializer,
    )
    def get(self, request: Request) -> Response:
        serializer = MeResponseSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    @extend_schema(
        tags=["accounts"],
        summary="회원 정보 수정",
        request=MeUpdateRequestSerializer,
        responses={200: MeUpdateResponseSerializer},
    )
    def patch(self, request: Request) -> Response:
        serializer = MeUpdateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_user = update_user_profile(user=request.user, validated_data=serializer.validated_data)  # type: ignore[arg-type]

        response_serializer = MeUpdateResponseSerializer(updated_user)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
