from django.urls import path

from apps.courses.views.admin.admin_course_view import (
    AdminCourseCreateAPIView,
    AdminCourseUpdateAPIView,
)
from apps.courses.views.admin.cohort_avg_scores_view import AdminCohortAvgScoresView
from apps.courses.views.admin.cohort_create_view import AdminCohortCreateView
from apps.courses.views.admin.cohort_students_view import AdminCohortStudentsView
from apps.courses.views.admin.cohort_update_view import AdminCohortUpdateView
from apps.courses.views.admin.subject_list_view import AdminSubjectListView
from apps.courses.views.admin.subject_scatter_view import AdminSubjectScatterView

urlpatterns = [
    # 기존 과정 API
    path("courses", AdminCourseCreateAPIView.as_view(), name="admin-course-create"),
    path("courses/<int:course_id>", AdminCourseUpdateAPIView.as_view(), name="admin-course-update"),
    path("cohorts", AdminCohortCreateView.as_view(), name="admin-cohort-create"),
    path("cohorts/<int:cohort_id>", AdminCohortUpdateView.as_view(), name="admin-cohort-update"),
    path(
        "courses/<int:course_id>/cohorts/avg-scores", AdminCohortAvgScoresView.as_view(), name="admin-cohort-avg-scores"
    ),
    path("cohorts/<int:cohort_id>/students", AdminCohortStudentsView.as_view(), name="admin-cohort-students"),
    path("courses/<int:course_id>/subjects", AdminSubjectListView.as_view(), name="admin-subject-list"),
    path("subjects/<int:subject_id>/scatter", AdminSubjectScatterView.as_view(), name="admin-subject-scatter"),
]
