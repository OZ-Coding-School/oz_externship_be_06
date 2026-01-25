# apps/users/urls/admin_urls.py
from django.urls import path

from apps.users.views.admin.account_views import AdminUserListView

urlpatterns = [
    # api/v1/admin/accounts 요청이 들어오면 바로 이 View로 연결됨
    path("", AdminUserListView.as_view(), name="admin-account-list"),
]
