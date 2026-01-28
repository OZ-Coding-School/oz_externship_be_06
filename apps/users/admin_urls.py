from django.urls import path
from rest_framework.permissions import BasePermission, IsAuthenticated

from apps.users.permissions import IsAdmin, IsAdminStaff
from apps.users.views.admin.admin_account_delete_views import AdminAccountDeleteAPIView
from apps.users.views.admin.admin_account_detail_views import AdminAccountDetailAPIView
from apps.users.views.admin.admin_account_role_views import (
    AdminAccountRoleUpdateAPIView,
)
from apps.users.views.admin.admin_account_views import AdminAccountUpdateAPIView
from apps.users.views.admin.admin_student_enrollment_views import (
    AdminStudentEnrollmentAcceptAPIView,
    AdminStudentEnrollmentListAPIView,
    AdminStudentEnrollmentRejectAPIView,
)
from apps.users.views.admin.admin_student_list_views import AdminStudentListAPIView
from apps.users.views.admin.admin_student_score_views import AdminStudentScoreAPIView


# GET, PATCH, DELETE를 같은 URL에서 처리하기 위한 combined view
class AdminAccountAPIView(AdminAccountDetailAPIView, AdminAccountUpdateAPIView, AdminAccountDeleteAPIView):
    # 어드민 회원 정보 조회/수정/삭제 API - GET: 조회, PATCH: 수정, DELETE: 삭제

    # 삭제는 어드민 권한만 가능하고 나머지는 관리자면 다 가능
    def get_permissions(self) -> list[BasePermission]:
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated(), IsAdminStaff()]


urlpatterns = [
    path(
        "accounts/<int:account_id>/",
        AdminAccountAPIView.as_view(),
        name="admin-account",
    ),
    path(
        "accounts/<int:account_id>/role/",
        AdminAccountRoleUpdateAPIView.as_view(),
        name="admin-account-role",
    ),
    path(
        "students/",
        AdminStudentListAPIView.as_view(),
        name="admin-student-list",
    ),
    path(
        "student-enrollments/",
        AdminStudentEnrollmentListAPIView.as_view(),
        name="admin-student-enrollment-list",
    ),
    path(
        "student-enrollments/accept",
        AdminStudentEnrollmentAcceptAPIView.as_view(),
        name="admin-student-enrollment-accept",
    ),
    path(
        "student-enrollments/reject",
        AdminStudentEnrollmentRejectAPIView.as_view(),
        name="admin-student-enrollment-reject",
    ),
    path(
        "students/<int:student_id>/scores",
        AdminStudentScoreAPIView.as_view(),
        name="admin-student-scores",
    ),
]
