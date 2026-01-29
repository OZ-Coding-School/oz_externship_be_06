from django.urls import path

from apps.courses.views.cohort_list_view import CohortListView
from apps.courses.views.course_view import CourseListAPIView

urlpatterns = [
    # 기존 과정 목록 조회
    path("course/", CourseListAPIView.as_view(), name="course-list"),
    # 110: 기수 리스트 조회 (일반 사용자)
    path("<int:course_id>/cohorts", CohortListView.as_view(), name="cohort-list"),
]
