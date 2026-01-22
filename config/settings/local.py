import os

from config.settings.base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

REST_FRAMEWORK.update(
    {
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.SessionAuthentication",  # 로컬에서 테스트 코드 동작시 force_login 작동을 위함
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        ),
    }
)

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

INTERNAL_IPS = [
    "127.0.0.1",
]

# 이메일 설정
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER") or ""
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD") or ""
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL") or EMAIL_HOST_USER
