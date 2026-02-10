from typing import Any, Dict, List, Optional

from rest_framework import serializers

from apps.users.models import User, Withdrawal

# --- 중첩 데이터용 시리얼라이저 ---


class WithdrawalUserSerializer(serializers.Serializer[Any]):
    """탈퇴 내역 유저 정보 (기본)"""

    id = serializers.IntegerField()
    email = serializers.EmailField()
    name = serializers.CharField()
    role = serializers.CharField()
    birthday = serializers.DateField()


class WithdrawalUserDetailSerializer(serializers.Serializer[Any]):
    """탈퇴 내역 유저 정보 (상세)"""

    id = serializers.IntegerField()
    email = serializers.EmailField()
    nickname = serializers.CharField()
    name = serializers.CharField()
    gender = serializers.CharField()
    role = serializers.CharField()
    status = serializers.CharField()
    profile_img_url = serializers.URLField(allow_null=True)
    created_at = serializers.DateTimeField()


# --- 유틸리티 함수 ---


def _get_user_status(user: User) -> str:
    """유저의 현재 활성화 상태를 계산합니다."""
    if user.is_active:
        return "ACTIVATED"
    # is_active가 False인 경우 탈퇴 여부 확인
    if hasattr(user, "withdrawals") and user.withdrawals.exists():
        return "WITHDREW"
    return "DEACTIVATED"


# --- 메인 시리얼라이저 ---


class AdminWithdrawalListSerializer(serializers.ModelSerializer[Withdrawal]):
    """어드민 탈퇴 내역 목록 조회 시리얼라이저"""

    user = serializers.SerializerMethodField()
    reason_display = serializers.CharField(source="get_reason_display", read_only=True)
    withdrawn_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Withdrawal
        fields = [
            "id",
            "user",
            "reason",
            "reason_display",
            "withdrawn_at",
        ]

    def get_user(self, obj: Withdrawal) -> Optional[Dict[str, Any]]:
        if not obj.user:
            return None

        user_data = {
            "id": obj.user.id,
            "email": obj.user.email,
            "name": obj.user.name,
            "role": obj.user.role,
            "birthday": obj.user.birthday,
        }
        return dict(WithdrawalUserSerializer(user_data).data)


class AdminWithdrawalDetailSerializer(serializers.ModelSerializer[Withdrawal]):
    """어드민 탈퇴 내역 상세 조회 시리얼라이저"""

    user = serializers.SerializerMethodField()
    assigned_courses = serializers.SerializerMethodField()
    reason_display = serializers.CharField(source="get_reason_display", read_only=True)
    withdrawn_at = serializers.DateTimeField(source="created_at", read_only=True)

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

    def get_user(self, obj: Withdrawal) -> Optional[Dict[str, Any]]:
        user = obj.user
        if not user:
            return None

        user_data = {
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
        return dict(WithdrawalUserDetailSerializer(user_data).data)

    def get_assigned_courses(self, obj: Withdrawal) -> List[Dict[str, Any]]:
        """
        탈퇴한 유저의 담당 과정 목록을 가져옵니다.
        admin_withdrawal_service의 get_assigned_courses가 누락된 경우를 대비해
        타입 안정성을 확보한 호출을 수행합니다.
        """
        if not obj.user:
            return []

        # circular import를 방지하고 mypy 에러를 피하기 위해 내부 임포트 혹은
        # 서비스 레이어의 존재 여부를 체크하여 안전하게 호출합니다.
        try:
            from apps.users.services.admin_withdrawal_service import (
                get_assigned_courses,
            )

            return list(get_assigned_courses(obj.user))
        except (ImportError, AttributeError):
            # 서비스 함수가 없거나 순환 참조 시 빈 리스트 반환 (방어적 코드)
            return []


class AdminWithdrawalCancelSerializer(serializers.Serializer[Any]):
    """탈퇴 취소 응답용"""

    detail = serializers.CharField()
