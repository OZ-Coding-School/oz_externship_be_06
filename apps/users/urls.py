from django.urls import path

from apps.users.views.change_phone_view import ChangePhoneView
from apps.users.views.course_view import AvailableCoursesAPIView, EnrolledCoursesAPIView
from apps.users.views.email_verification_view import (
    SendEmailVerificationAPIView,
    VerifyEmailAPIView,
)
from apps.users.views.enroll_student_view import EnrollStudentAPIView
from apps.users.views.find_email_view import FindEmailAPIView
from apps.users.views.login_view import LoginAPIView, LogoutAPIView
from apps.users.views.me import MeView
from apps.users.views.password_view import ChangePasswordAPIView, FindPasswordAPIView
from apps.users.views.profile_image_view import ProfileImageView
from apps.users.views.restore_view import RestoreAPIView
from apps.users.views.sign_up_view import SignUpAPIView, SignupNicknameCheckAPIView
from apps.users.views.sms_verification_view import (
    SendSmsVerificationAPIView,
    VerifySmsAPIView,
)
from apps.users.views.social_login_view import (
    KakaoCallbackAPIView,
    KakaoLoginStartAPIView,
    NaverCallbackAPIView,
    NaverLoginStartAPIView,
)
from apps.users.views.token_refresh_view import TokenRefreshAPIView
from apps.users.views.withdrawal_view import WithdrawalAPIView

urlpatterns = [
    # 회원가입
    path("signup/", SignUpAPIView.as_view(), name="signup"),
    path("check-nickname/", SignupNicknameCheckAPIView.as_view(), name="check-nickname"),
    # 이메일 인증
    path("verification/send-email/", SendEmailVerificationAPIView.as_view(), name="send-email-verification"),
    path("verification/verify-email/", VerifyEmailAPIView.as_view(), name="verify-email"),
    # SMS 인증
    path("verification/send-sms/", SendSmsVerificationAPIView.as_view(), name="send-sms-verification"),
    path("verification/verify-sms/", VerifySmsAPIView.as_view(), name="verify-sms"),
    # 내 정보
    path("me/", MeView.as_view(), name="me"),
    path("me/profile-image/", ProfileImageView.as_view(), name="profile-image"),
    path("me/refresh/", TokenRefreshAPIView.as_view(), name="token-refresh"),
    # 로그인/로그아웃
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    # 비밀번호
    path("change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path("find-password/", FindPasswordAPIView.as_view(), name="find-password"),
    # 이메일 찾기
    path("find-email/", FindEmailAPIView.as_view(), name="find-email"),
    # 휴대폰 번호 변경
    path("change-phone/", ChangePhoneView.as_view(), name="change-phone"),
    # 수강생 등록 신청
    path("enroll-student/", EnrollStudentAPIView.as_view(), name="enroll-student"),
    # 수강 관련
    path("available-courses/", AvailableCoursesAPIView.as_view(), name="available-courses"),
    path("me/enrolled-courses/", EnrolledCoursesAPIView.as_view(), name="enrolled-courses"),
    path("withdrawal/", WithdrawalAPIView.as_view(), name="withdrawal"),
    path("restore/", RestoreAPIView.as_view(), name="restore"),
    # 소셜 로그인
    path("login/kakao/", KakaoLoginStartAPIView.as_view(), name="kakao-login-start"),
    path("login/kakao/callback/", KakaoCallbackAPIView.as_view(), name="kakao-login-callback"),
    path("login/naver/", NaverLoginStartAPIView.as_view(), name="naver-login-start"),
    path("login/naver/callback/", NaverCallbackAPIView.as_view(), name="naver-login-callback"),
]
