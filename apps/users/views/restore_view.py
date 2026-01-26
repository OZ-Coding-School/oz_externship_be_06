from datetime import date

from django.contrib.auth import get_user_model
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models.withdrawal import Withdrawal
from apps.users.serializers.restore_serializer import (
    RestoreErrorDetailSerializer,
    RestoreSerializer,
    RestoreSuccessSerializer,
)
from apps.users.utils.redis_utils import delete_email_token, get_email_by_token

User = get_user_model()


class RestoreAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="탈퇴 계정 복구 API",
        request=RestoreSerializer,
        responses={
            200: RestoreSuccessSerializer,
            404: RestoreErrorDetailSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = RestoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_token = serializer.validated_data["email_token"]
        email = get_email_by_token(email_token)

        if not email:
            return Response({"error_detail": "유효하지 않은 인증 토큰입니다."}, status=status.HTTP_404_NOT_FOUND)

        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"error_detail": "복구할 계정을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        withdrawal = Withdrawal.objects.filter(user=user).first()

        if not withdrawal:
            return Response({"error_detail": "복구할 탈퇴 계정을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        if withdrawal.due_date < date.today():
            return Response(
                {"error_detail": "복구 가능 기간이 만료되었습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        with transaction.atomic():
            user.is_active = True
            user.save(update_fields=["is_active"])
            withdrawal.delete()
            delete_email_token(email_token)

        return Response({"detail": "계정복구가 완료되었습니다."}, status=status.HTTP_200_OK)
