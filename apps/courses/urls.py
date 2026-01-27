from django.urls import path

from apps.courses.views.course_view import CourseListAPIView

urlpatterns = [
    path("", CourseListAPIView.as_view(), name="course-list"),
]
