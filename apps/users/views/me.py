from typing import TYPE_CHECKING, cast

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.me import MeResponseSerializer

if TYPE_CHECKING:
    from apps.users.models import User as UserModel


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Accounts"],
        summary="내 정보 조회",
        responses=MeResponseSerializer,
    )
    def get(self, request: Request) -> Response:
        user = cast("UserModel", request.user)

        serializer = MeResponseSerializer(user, context={"request": request})
        return Response(serializer.data)
