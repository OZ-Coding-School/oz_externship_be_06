from django.urls import path

from rest_framework.permissions import BasePermission, IsAuthenticated

from apps.users.permissions import IsAdmin, IsAdminStaff
from apps.users.views.admin.admin_account_delete_views import AdminAccountDeleteAPIView
from apps.users.views.admin.admin_account_detail_views import AdminAccountDetailAPIView
from apps.users.views.admin.admin_account_views import AdminAccountUpdateAPIView


# GET, PATCH, DELETE를 같은 URL에서 처리하기 위한 combined view
class AdminAccountAPIView(AdminAccountDetailAPIView, AdminAccountUpdateAPIView, AdminAccountDeleteAPIView):
    """어드민 회원 정보 조회/수정/삭제 API (GET: 조회, PATCH: 수정, DELETE: 삭제)."""

    def get_permissions(self) -> list[BasePermission]:
        """DELETE는 ADMIN만, 나머지는 스태프도 가능."""
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated(), IsAdminStaff()]


urlpatterns = [
    path(
        "accounts/<int:account_id>/",
        AdminAccountAPIView.as_view(),
        name="admin-account",
    ),
]
