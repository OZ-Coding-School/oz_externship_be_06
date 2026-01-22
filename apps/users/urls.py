from django.urls import path

from apps.users.views.email_verification_view import (
    SendEmailVerificationAPIView,
    VerifyEmailAPIView,
)
from apps.users.views.sign_up_view import SignUpAPIView, SignupNicknameCheckAPIView

urlpatterns = [
    # 회원가입
    path("signup/", SignUpAPIView.as_view(), name="signup"),
    path("check-nickname/", SignupNicknameCheckAPIView.as_view(), name="check-nickname"),
    # 이메일 인증
    path("verification/send-email/", SendEmailVerificationAPIView.as_view(), name="send-email-verification"),
    path("verification/verify-email/", VerifyEmailAPIView.as_view(), name="verify-email"),
]
