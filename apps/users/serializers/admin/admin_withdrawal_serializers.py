from typing import Any

from rest_framework import serializers

from apps.users.models import User, Withdrawal
from apps.users.services.admin_withdrawal_service import get_assigned_courses


# 탈퇴 내역 유저 정보
class WithdrawalUserSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    name = serializers.CharField()
    role = serializers.CharField()
    birthday = serializers.DateField()


#유저 상태 계산
def _get_user_status(user: User) -> str:
    if user.is_active:
        return "ACTIVATED"
    # is_active가 False인 경우
    if hasattr(user, "withdrawal") and user.withdrawal:
        return "WITHDREW"
    return "DEACTIVATED"


# 어드민 탈퇴 내역 목록 조회
class AdminWithdrawalListSerializer(serializers.ModelSerializer[Withdrawal]):
    user = serializers.SerializerMethodField()
    reason = serializers.CharField()
    reason_display = serializers.SerializerMethodField()
    withdrawn_at = serializers.DateTimeField(source="created_at")

    class Meta:
        model = Withdrawal
        fields = [
            "id",
            "user",
            "reason",
            "reason_display",
            "withdrawn_at",
        ]

    def get_user(self, obj: Withdrawal) -> dict[str, Any] | None:
        if not obj.user:
            return None
        return {
            "id": obj.user.id,
            "email": obj.user.email,
            "name": obj.user.name,
            "role": obj.user.role,
            "birthday": obj.user.birthday,
        }

    def get_reason_display(self, obj: Withdrawal) -> str:
        return obj.get_reason_display()


#어드민 탈퇴 내역 상세 조회
class AdminWithdrawalDetailSerializer(serializers.ModelSerializer[Withdrawal]):
    user = serializers.SerializerMethodField()
    assigned_courses = serializers.SerializerMethodField()
    reason = serializers.CharField()
    reason_display = serializers.SerializerMethodField()
    reason_detail = serializers.CharField()
    due_date = serializers.DateField()
    withdrawn_at = serializers.DateTimeField(source="created_at")

    class Meta:
        model = Withdrawal
        fields = [
            "id",
            "user",
            "assigned_courses",
            "reason",
            "reason_display",
            "reason_detail",
            "due_date",
            "withdrawn_at",
        ]

    def get_user(self, obj: Withdrawal) -> dict[str, Any] | None:
        if not obj.user:
            return None
        user = obj.user
        return {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "name": user.name,
            "gender": user.gender,
            "role": user.role,
            "status": _get_user_status(user),
            "profile_img_url": user.profile_img_url,
            "created_at": user.created_at,
        }

    def get_assigned_courses(self, obj: Withdrawal) -> list[dict[str, Any]]:
        if not obj.user:
            return []
        return get_assigned_courses(obj.user)

    def get_reason_display(self, obj: Withdrawal) -> str:
        return obj.get_reason_display()


#어드민 탈퇴 취소
class AdminWithdrawalCancelSerializer(serializers.Serializer[Any]):
    detail = serializers.CharField()
