from django.urls import path
from apps.posts.views.category_views import CategoryListView
from apps.posts.views.post_views import PostCreateView

urlpatterns = [
    path('categories', CategoryListView.as_view(), name="category-list"),
    path('',PostCreateView.as_view(), name='post-create'),
]