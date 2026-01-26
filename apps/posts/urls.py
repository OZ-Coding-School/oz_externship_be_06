from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.post_views import PostViewSet
from .views.post_category_views import PostCategoryListView

router = DefaultRouter()
router.register(r"", PostViewSet, basename="post")

urlpatterns = [
    path("categories/", PostCategoryListView.as_view(), name="category-list"),
    path("", include(router.urls)),
]