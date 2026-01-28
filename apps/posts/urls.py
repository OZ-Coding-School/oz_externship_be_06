from django.urls import path

from apps.posts.views.post_category_views import PostCategoryListAPIView

urlpatterns = [
    path("categories/", PostCategoryListAPIView.as_view(), name="post-category-list"),
]
