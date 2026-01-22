from django.urls import path

from apps.users.views.email_verification_view import (
    SendEmailVerificationAPIView,
    VerifyEmailAPIView,
)
from apps.users.views.me import Meview
from apps.users.views.login_view import LoginAPIView, LogoutAPIView
from apps.users.views.sign_up_view import SignUpAPIView, SignupNicknameCheckAPIView

urlpatterns = [
    # 회원가입
    path("signup/", SignUpAPIView.as_view(), name="signup"),
    path("check-nickname/", SignupNicknameCheckAPIView.as_view(), name="check-nickname"),
    # 이메일 인증
    path("verification/send-email/", SendEmailVerificationAPIView.as_view(), name="send-email-verification"),
    path("verification/verify-email/", VerifyEmailAPIView.as_view(), name="verify-email"),
    # 내 정보
    path("me/", Meview.as_view(), name="me"),
    # 로그인/로그아웃
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]