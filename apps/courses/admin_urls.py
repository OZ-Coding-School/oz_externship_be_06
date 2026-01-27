from django.urls import path

from apps.courses.views.admin.admin_course_view import (
    AdminCourseCreateAPIView,
    AdminCourseUpdateAPIView,
)

urlpatterns = [
    path("", AdminCourseCreateAPIView.as_view(), name="admin-course-create"),
    path("<int:course_id>/", AdminCourseUpdateAPIView.as_view(), name="admin-course-update"),
]
