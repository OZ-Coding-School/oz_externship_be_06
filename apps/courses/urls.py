from django.urls import path

from apps.courses.views.cohort_list_view import CohortListView
from apps.courses.views.course_view import CourseListAPIView

urlpatterns = [
    # 기존 과정 목록 조회
    path("course/", CourseListAPIView.as_view(), name="course-list"),

    path("<int:course_id>/cohorts", CohortListView.as_view(), name="cohort-list"),
]
