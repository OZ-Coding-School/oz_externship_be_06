from typing import TYPE_CHECKING, cast
from urllib.request import Request

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

if TYPE_CHECKING:
    from apps.users.models import User as UserModel


class Meview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        user = cast("UserModel", request.user)  # type: ignore[attr-defined]
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "name": user.name,
                "phone_number": user.phone_number,
                "birthday": user.birthday.isoformat() if user.birthday else None,
                "gender": "M" if user.gender == "MALE" else "F",
                "profile_img_url": user.profile_img_url,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
        )
