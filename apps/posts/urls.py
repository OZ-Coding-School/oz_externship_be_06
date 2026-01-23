from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.post_views import PostViewSet
from .views.post_category_views import PostCategoryListView

# ViewSet을 주소와 연결해주는 라우터 설정입니다.
router = DefaultRouter()
router.register(r"community", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)), # /api/v1/posts/community/ 주소가 됩니다.
    path("categories/", PostCategoryListView.as_view(), name="category-list"), # /api/v1/posts/categories/ 주소가 됩니다.
]