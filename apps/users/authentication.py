from typing import Any

from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class ActiveUserJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token: Any) -> object:  # type: ignore[override]
        user = super().get_user(validated_token)

        if not getattr(user, "is_active", True):
            raise AuthenticationFailed(
                detail={"error_detail": {"detail": "비활성화된 계정입니다."}},
                code="inactive_user",
            )

        return user
