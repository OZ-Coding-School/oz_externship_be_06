from django.urls import path
from rest_framework.permissions import BasePermission, IsAuthenticated

from apps.users.permissions import IsAdmin, IsAdminStaff
from apps.users.views.admin.account_views import AdminUserListView
from apps.users.views.admin.admin_account_delete_views import AdminAccountDeleteAPIView
from apps.users.views.admin.admin_account_detail_views import AdminAccountDetailAPIView
from apps.users.views.admin.admin_account_role_views import (
    AdminAccountRoleUpdateAPIView,
)
from apps.users.views.admin.admin_account_views import AdminAccountUpdateAPIView
from apps.users.views.admin.admin_analytics_views import (
    AdminSignupTrendsAPIView,
    AdminWithdrawalReasonCountsAPIView,
    AdminStudentEnrollmentTrendsAPIView,
    AdminWithdrawalTrendsAPIView,
)
from apps.users.views.admin.admin_student_enrollment_views import (
    AdminStudentEnrollmentAcceptAPIView,
    AdminStudentEnrollmentListAPIView,
    AdminStudentEnrollmentRejectAPIView,
)
from apps.users.views.admin.admin_student_list_views import AdminStudentListAPIView
from apps.users.views.admin.admin_student_score_views import AdminStudentScoreAPIView
from apps.users.views.admin.admin_withdrawal_views import (
    AdminWithdrawalDetailAPIView,
    AdminWithdrawalListAPIView,
)


# GET, PATCH, DELETE를 같은 URL에서 처리하기 위한 combined view
class AdminAccountAPIView(AdminAccountDetailAPIView, AdminAccountUpdateAPIView, AdminAccountDeleteAPIView):
    # 어드민 회원 정보 조회/수정/삭제 API - GET: 조회, PATCH: 수정, DELETE: 삭제

    # 삭제는 어드민 권한만 가능하고 나머지는 관리자면 다 가능
    def get_permissions(self) -> list[BasePermission]:
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated(), IsAdminStaff()]


urlpatterns = [
    #  어드민 회원 목록 조회
    path(
        "accounts/",
        AdminUserListView.as_view(),
        name="admin-account-list",
    ),
    # 어드민 회원 상세/수정/삭제
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
    # Students
    path("students/", AdminStudentListAPIView.as_view(), name="admin-student-list"),
    path("students/<int:student_id>/scores", AdminStudentScoreAPIView.as_view(), name="admin-student-scores"),
    path("student-enrollments/", AdminStudentEnrollmentListAPIView.as_view(), name="admin-student-enrollment-list"),
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
    # Withdrawals
    path("withdrawals/", AdminWithdrawalListAPIView.as_view(), name="admin-withdrawal-list"),
    path("withdrawals/<int:withdrawal_id>/", AdminWithdrawalDetailAPIView.as_view(), name="admin-withdrawal-detail"),
    # Analytics
    path("analytics/signup/trends", AdminSignupTrendsAPIView.as_view(), name="admin-signup-trends"),
    path(
        "analytics/withdrawals/trends/",
        AdminWithdrawalTrendsAPIView.as_view(),
        name="admin-withdrawal-trends",
    ),
    path(
        "analytics/student-enrollments/trends/",
        AdminStudentEnrollmentTrendsAPIView.as_view(),
        name="admin-student-enrollment-trends",
    ),
    path(
        "analytics/withdrawals/reasons/counts/",
        AdminWithdrawalReasonCountsAPIView.as_view(),
        name="admin-withdrawal-reason-counts",
    ),
]
