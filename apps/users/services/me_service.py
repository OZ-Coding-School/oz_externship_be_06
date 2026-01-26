from typing import Any

from django.core.files.uploadedfile import UploadedFile
from django.db import IntegrityError

from apps.users.models import User
from apps.users.utils.redis_utils import delete_sms_token, get_phone_by_token


# 이미 등록된 휴대폰 번호 예외
class PhoneNumberAlreadyExistsError(Exception):
    pass


# 유효하지 않은 휴대폰 인증 토큰 예외
class InvalidPhoneTokenError(Exception):

    pass


# 내정보 수정
def update_user_profile(*, user: User, validated_data: dict[str, Any]) -> User:
    gender_map = {"M": "MALE", "F": "FEMALE"}

    if "gender" in validated_data:
        validated_data["gender"] = gender_map.get(validated_data["gender"], validated_data["gender"])

    for field, value in validated_data.items():
        setattr(user, field, value)

    user.save(update_fields=list(validated_data.keys()) + ["updated_at"])
    return user


# 프로필 이미지 수정 - S3
def update_profile_image(*, user: User, image: UploadedFile) -> User:
    from apps.core.utils.s3 import S3Client

    s3 = S3Client()

    # 기존 이미지 삭제
    if user.profile_img_url:
        s3.delete_by_url(user.profile_img_url)

    # 새 이미지 업로드
    key = s3.upload(image, path_prefix="profile")
    user.profile_img_url = s3.build_url(key)
    user.save(update_fields=["profile_img_url", "updated_at"])
    return user


# 휴대폰 번호 변경
def change_phone_number(*, user: User, phone_verify_token: str) -> User:
    # 토큰조회
    phone_number = get_phone_by_token(phone_verify_token)

    if not phone_number:
        raise InvalidPhoneTokenError("유효하지 않거나 만료된 인증 토큰입니다.")

    # 중복 체크
    if User.objects.filter(phone_number=phone_number).exclude(id=user.id).exists():
        raise PhoneNumberAlreadyExistsError("이미 등록된 휴대폰 번호입니다.")

    # 휴대폰 번호 변경
    user.phone_number = phone_number
    try:
        user.save(update_fields=["phone_number", "updated_at"])
    except IntegrityError:
        raise PhoneNumberAlreadyExistsError("이미 등록된 휴대폰 번호입니다.")

    # 토큰 삭제
    delete_sms_token(phone_verify_token)

    return user
