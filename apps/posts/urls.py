from django.urls import path
from apps.posts.views.category_views import CategoryListView

urlpatterns = [
    path('categories', CategoryListView.as_view(), name="category-list"),
]