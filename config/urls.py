from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    #  Admin API
    path("api/v1/admin/", include("apps.users.admin_urls")),
    path("api/v1/admin/", include("apps.courses.admin_urls")),
    path("api/v1/admin/", include("apps.exams.urls.admin")),
    path("api/v1/admin/", include("apps.qna.urls.admin")),
    # General API
    path("api/v1/accounts/", include("apps.users.urls")),
    path("api/v1/", include("apps.courses.urls")),
    path("api/v1/exams/", include("apps.exams.urls.student")),
    path("api/v1/posts/", include("apps.posts.urls", "posts")),
    path("api/v1/chatbot/", include("apps.chatbot.urls")),
    path("api/v1/qna/", include("apps.qna.urls.general")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if "debug_toolbar" in settings.INSTALLED_APPS:
        urlpatterns += [
            path("debug/", include("debug_toolbar.urls")),
        ]

    if "drf_spectacular" in settings.INSTALLED_APPS:
        urlpatterns += [
            path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
            path(
                "api/schema/swagger-ui/",
                SpectacularSwaggerView.as_view(url_name="schema"),
                name="swagger-ui",
            ),
            path(
                "api/schema/redoc/",
                SpectacularRedocView.as_view(url_name="schema"),
                name="redoc",
            ),
        ]
